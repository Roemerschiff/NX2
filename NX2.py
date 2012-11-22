# -*- coding: utf-8 -*-
import os
import datetime
import itertools
import warnings

import numpy as np
import scipy
import scipy.interpolate
import scipy.stats
import scipy.odr
from scipy.signal import convolve
from scipy.io.idl import readsav
import matplotlib.pylab as plt
import matplotlib
import matplotlib.dates

import asciitable
import atpy

mps2knots = 0.51444  # factor to convert m/s to knots

def smooth_expdec(data, t_e):
    '''smooth an array with an exponential decay

    :param data: input array to be smoothed
    :param t_e: decay timescale of expoential in number of bins
        (for NX2 data, i.e. seconds)'''
    kernel = np.zeros(2*3*t_e+1)
    kernel[3*t_e:] = np.exp(-np.arange(3*t_e)/t_e)
    kernel = kernel / kernel.sum()
    return convolve(data,kernel,'same')

def smooth_gauss(data, width):
    '''smooth an array with a gauss

    :param data: input array to be smoothed
    :param width: width of gauss distribution in number of bins
        (for NX2 data, i.e. seconds)'''
    norm = scipy.stats.norm(0.,width)
    kernel = norm.pdf(np.arange(-3.*width,3.001*width))
    kernel = kernel / kernel.sum()
    return convolve(data,kernel,'same')

#TBD: ideas for further development
#   read_NX2: define proper timezone instead of timeoffset

def read_NX2(self, filename, date, corr_bsp = 1.,origin = None, timeoffset = 2):
    '''read in csv data and initialize table
    
    :param filename: filename as string or other input compatible with asciitable
    :param date: date of measurement
    :type date: tuple of integers ``(day, month, year)``
    :keyword corr_bsp: multiplictive correction factor for BSP
    :keyword origin:tuple (lat, lon) in deg of x,y origin
        default: lat, lon at first datapoint
    :keyword timeoffset: hours to be added to convert UT to local
    '''
    include_names = ['TIME', 'LAT', 'LON', 'AWA', 'AWS', 'BSP', 'COG', 'DFT', 'HDC', 'SET', 'SOG', 'TWA', 'TWS']
    converters = {'TIME': asciitable.convert_list(float)}

    try:
        atpy.Table.__init__(self, filename, type='ascii', delimiter=',', fill_values=('','nan'), data_start = 5, include_names = include_names, guess = False)
        print 'Reading new format NX2 table - Export with 1.08'
    except asciitable.InconsistentTableError:
        print 'Reading NX2 table, which was exported with 1.05'
        #30 header values, but only 29 table entries, manually delete the last header value
        names = ['DATE', 'TIME', 'LAT', 'LON', 'AWA', 'AWS', 'BOD', 'BSP', 'BTW', 'CMG', 'COG', 'CTS', 'DEP', 'DFT', 'DMG', 'DST', 'DTW', 'HDC', 'LOG', 'RDR', 'SET', 'SOG', 'TBS', 'TEMP', 'TWA', 'TWS', 'VAR', 'VMG', 'WCV']
        atpy.Table.__init__(self, filename, type='ascii', delimiter=',', names=names, fill_values=('','nan'), data_start = 5, include_names = include_names)
    
    self.read_date=date
    self.filename = filename
    if origin: 
        self.origin = origin
    else:    
        self.origin = (self.LAT[0], self.LON[0])
        
    # remove all columns which contain only NaNs
    # interpolate nans in those columns with only a few nans
    for name in self.names:
        valid = np.isfinite(self[name])
        if valid.all():
            pass
        elif (~valid).all():
            self.remove_columns(name)
        elif (np.sum(valid, dtype=np.float)/ len(valid)) >= 0.98:
            self.fill_nans(name)
        elif name == 'TIME':
            print 'Warning: TIME contains > 2 % nans. Interpolating ...'
            self.fill_nans(name)
        else:
            print 'Warning: column '+ name + ' contains more than 2% nans. No automatic interpolation performed.'  

    self.add_empty_column('year', np.int_)
    self.add_empty_column('month', np.int_)
    self.add_empty_column('day', np.int_)
    self.add_empty_column('hour', np.int_)
    self.add_empty_column('minute', np.int_)
    self.add_empty_column('sec', np.int_)
    self.year[:] = date[2]
    self.month[:] = date[1]
    self.day[:] = date[0]
    # TBD: self.TIME has non-unique entries
    # change [1,1,1] -> [1,1.33,1.66] ? Needs sub-s times then
    TIME = timeoffset * 3600 + self.TIME
    h,m,s = sec2hms(TIME)
    self.hour[:] = h
    self.minute[:] = m
    self.sec[:] = s

    r_earth=6300e3  #in Si unit - meter
    self.add_column('y', 2.*np.pi*r_earth/360.*(self.LAT-self.origin[0]))
    self.add_column('x', 2.*np.pi*r_earth*np.cos(self.LAT/180.*np.pi)/360.*(self.LON-self.origin[1]))

    self.BSP = self.BSP * corr_bsp
    #self.write_kml(self.filename+'.kml')

atpy.register_reader('nx2', read_NX2, override = True)

def sec2hms(sec):
    h, rest = divmod(sec,3600)
    m, rest = divmod(rest, 60)
    s, rest = divmod(rest, 1)
    return h, m, s

    
def write_leg(data, kmlFile, ind, name ='', style = '#yellowLine', skip = 1):
    '''write one leg of the journel to a kml file.

    This does not write complete kml files, neither does it open the
    file!

    Parameters:
    -----------
    data : NX2 instance
        `LAT` and `LON` are taken from this instance.
    kmlFile : file handle
    ind : index array
        indexed values are written in this leg
    name : string , optional
        Name of this leg in kml file
    style : string , optional
        name of a line stype defined in the kml header
    skip : ind
        Skips `skip` values befroe a new position is written.
        Use for coarser, but smaller files.
    '''
    LAT = data.LAT[ind]
    LON = data.LON[ind]
    latchange = np.hstack([True,np.diff(LAT) != 0.])
    lonchange = np.hstack([True,np.diff(LON) != 0.])
    change = (latchange | lonchange).nonzero()
    kmlFile.write('      <Placemark>')
    kmlFile.write('        <name>'+name+'</name>')
    kmlFile.write('        <description>Start:'+str(data.datetime()[ind[0]]) +'</description>')
    kmlFile.write('        <styleUrl>'+style+'</styleUrl>')
    kmlFile.write('        <LineString>')
    kmlFile.write('          <extrude>1</extrude>')
    kmlFile.write('          <tessellate>1</tessellate>')
    kmlFile.write('          <altitudeMode>absolute</altitudeMode>')
    kmlFile.write('          <coordinates>\n')
    for i in change[0][::skip]:
        kmlFile.write('          {0:10.7f}, {1:10.7f}\n'.format(LON[i], LAT[i]))
    kmlFile.write('        </coordinates>')
    kmlFile.write('      </LineString>')
    kmlFile.write('    </Placemark>\n')

class OriginError(Exception):
    pass
    
# import NX2
# dat = NX2.NX2Table('../data/18tue_firstday.00.csv', (18,5,2009))
# dat = NX2.NX2Table('../2008/080424eleventhday_sail.00.csv', (24,4,2008))
class NX2Table(atpy.Table):
  
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            raise ValueError('Filename and date tuple required.')
        if len(args) > 1:
            kwargs['type'] = 'NX2'
        atpy.Table.__init__(self, *args, **kwargs)
    
    def datetime(self):
        return np.array(map(datetime.datetime, self.year, self.month, self.day, self.hour, self.minute, self.sec))

    def time(self):
        return np.array(map(datetime.time, self.hour, self.minute, self.sec))
    
    def fill_nans(self, column):
        index = np.isfinite(self[column])
        print "Interpolating over missing values in column " + column
        print "Maximum data gap is ", str(max([len(list(v)) for g,v in itertools.groupby(index) if not g])), 'lines'
        if column == 'TIME':
            x = np.arange(len(self),dtype = np.float)
            func = scipy.interpolate.interp1d(x[index],self[column][index], bounds_error = False)
            self[column][~index] = func(x[~index])
        else:
            func = scipy.interpolate.interp1d(self.TIME[index],self[column][index], bounds_error = False)
            self[column][~index] = func(self.TIME[~index])

    def where(self, mask):
        new_table = atpy.Table.where(self, mask)
        new_table.origin = self.origin
        new_table.read_date = self.read_date
        return new_table
        
    def when(self, t1=(0,0,0),t2=(23,59,59)):
        ind = (self.time() >= datetime.time(*t1)) & (self.time() <= datetime.time(*t2))
        return self.where(ind)
    
    def fit_BSP_corr(self):
        '''fit a linear correlation between BSP and SOG
        
        Only points which fullfill the following criteria are used:
        
            - BSP > 0
            - |COG-HDC| < 15
            - small gradients in speed
        
        Returns
        -------
        myoutput : scipy.odr.odrpack.Output object
            contains the fit results
        con : boolean array
            index array of points usef for fitting
        '''
        def line(B, x):
            ''' Linear function y = m*x + b '''
            return B[0] *x
        
        con1 = (self.BSP > 0)  #moving
        con2 = (np.abs(self.COG - self.HDC) < 15.)
        #SOG and BSP have different resonse times -> ignore gradients
        smoothed = smooth_gauss(self.BSP, 3.)
        con3 = (abs(np.diff(smoothed)) < 0.01) # careful! n-1 elements!
        myl = con3.tolist()
        myl.append([True])
        con3 = np.array(myl)
        con = con1 & con2 & con3
        linear = scipy.odr.Model(line)
        mydata = scipy.odr.RealData(self.SOG[con],self.BSP[con])
        myodr = scipy.odr.ODR(mydata, linear, beta0 = [1.])
        myoutput = myodr.run()
        return myoutput, con


    def plot_course(self, scale = 50, n = 300):
        plt.clf()
        plt.plot(self.x, self.y,'k')
        # overplot path with saling in blue
        if 'sailing' in self.keys():
            # make groups of indices with the sail up
            for sail, ind in itertools.groupby(range(len(self)), key = lambda a:self.sailing[a]):
                if sail ==1 :
                  index = list(ind)
                  plt.plot(self.x[index], self.y[index],'b')
        wind_v = self.TWS / mps2knots
        wind_ang = self.AWA + self.HDC + 180.
        quiver_wind = plt.quiver(self.x[::n],self.y[::n], self.TWS[::n]*np.sin(wind_ang[::n]/180.*np.pi), self.TWS[::n]*np.cos(wind_ang[::n]/180.*np.pi), scale = scale, color= 'g')
        quiver_bsp  = plt.quiver(self.x[::n],self.y[::n], self.BSP[::n]*np.sin(self.HDC[::n]/180.*np.pi), self.BSP[::n]*np.cos(self.HDC[::n]/180.*np.pi), scale = scale)
        quiver_sog  = plt.quiver(self.x[::n],self.y[::n], self.SOG[::n]*np.sin(self.COG[::n]/180.*np.pi), self.SOG[::n]*np.cos(self.COG[::n]/180.*np.pi), scale = scale, color= 'b')
        if scale == None:
            qk_scale = None
        else:
            qk_scale = scale/20.
        qk_wind = plt.quiverkey(quiver_wind, .1, 0.95, qk_scale, 'Wind', labelpos='E')
        qk_bsp = plt.quiverkey(quiver_bsp, .1, 0.9, qk_scale, 'Bewegung gegen Wasser', labelpos='E')
        qk_sog = plt.quiverkey(quiver_sog, .1, 0.85, qk_scale, u'Bewegung über Grund', labelpos='E')
        plt.xlabel('West - Ost [Meter]')
        plt.ylabel('Sued - Nord [Meter]')
        
    def plot_speeds(self, t1=(0,0,0),t2=(23,59,59)):
        fig = plt.figure()
        fig.canvas.set_window_title('Bootsgeschwindigkeit')
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M', tz=None))
        #plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

        ind = (self.time() >= datetime.time(*t1)) & (self.time() <= datetime.time(*t2))

        sog = ax.plot(self.datetime()[ind], self.SOG[ind], label='SOG')
        bsp = ax.plot(self.datetime()[ind], self.BSP[ind], label='BSP')
        xlab = ax.get_xticklabels()
        for label in xlab: label.set_rotation(30)
        lab = plt.ylabel('Geschwindigkeit in Knoten')
        lab = plt.xlabel('Uhrzeit')
        
        if 'sailing' in self.keys():
            #sailind = (ind & (self.sailing == 1))
            sail = ax.plot(self.datetime()[ind], self.sailing[ind], 'bs', label = 'Sailing')
        #plt.xticks(rotation=45)
        if 'rowpermin' in self.keys():
            ax2 = ax.twinx()
            index = self.minutes_index() & ind
            minutes = np.array(map(lambda x: x.replace(second = 0, microsecond=0),self.datetime()[index]))
            row = ax2.bar(minutes, self.rowpermin[index], label=u'Ruderschläge', width=1./24./60., linewidth = 0., alpha = 0.4, color='r')
            ax2.set_ylabel(u'Ruderschläge', color='r')
            ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M', tz=None))
            for tl in ax2.get_yticklabels():
                tl.set_color('r') 

        return fig
    
        
    def add_rowing_old_format(self, filename):
        '''add rowing and sailing data
        
        :input: filename for cvs file in format as used in 2008
        '''
        print 'Be careful: Input data does not contain info on month and year.'
        rowdata = atpy.Table(filename, type = 'ascii', delimiter = ';')
        #rowtime = np.array(map(lambda x: datetime.datetime(self.read_date[2],self.read_date[1],*x), zip(rowdata['Tag'], rowdata['Stunde'], rowdata['Minute'])))
        if 'Ruderschlaege/Minute' in rowdata.keys():
            print 'Load rowing data'
            if 'rowpermin' in self.keys():
                print 'Updating rowing data'
            else:    
                self.add_empty_column('rowpermin', dtype = '<i4', null = 0)
        if 'Segel' in rowdata.keys():
            print 'Load sailing data'
            if 'sailing' in self.keys():
                print 'Updating sailing data'
            else:    
                self.add_empty_column('sailing', dtype = '<i4', null = 0)
                
        for i in range(len(rowdata)):
            ind = (self.day == rowdata.Tag[i]) & (self.hour == rowdata.Stunde[i]) & (self.minute == rowdata.Minute[i])
            #ind = (self.datetime() >= rowtime[i]) & (self.datetime() <= (rowtime[i] + datetime.timedelta(0,60)))
            if 'rowpermin' in self.keys():
                try:
                    self.rowpermin[ind] = rowdata['Ruderschlaege/Minute'][i]
                except ValueError:
                    pass
            if 'sailing' in self.keys():
                self.sailing[ind] = rowdata['Segel'][i]
        #self.write_kml(self.filename+'.kml')
        
    def add_schwaller(self):
        '''read Schwaller file with flow speed and add column to data'''
        if np.abs(self.origin[0]-49.0164) > 0.0001:
            raise OriginError('Lattitude of origin does not match origin of Schwaller data')
        if np.abs(self.origin[1]-12.0285) > 0.0001:
            raise OriginError('Longitude of origin does not match origin of Schwaller data')      
        
        schwaller = readsav(os.path.join(os.path.dirname(__file__), 'stromgeschwindigkeit.sav'))['strom']
        xy = np.vstack((schwaller['X'][0],schwaller['Y'][0])).transpose()
        schwallervx = scipy.interpolate.NearestNDInterpolator(xy, schwaller['VX'][0])
        schwallervy = scipy.interpolate.NearestNDInterpolator(xy, schwaller['VY'][0])
        selfxy = np.vstack((self.x, self.y)).transpose()
        self.add_column('stromwo', schwallervx(selfxy)/mps2knots)
        self.add_column('stromsn', schwallervy(selfxy)/mps2knots)
        self.add_column('vx_wassys', self.SOG*np.sin(np.deg2rad(self.COG))-self.stromwo)
        self.add_column('vy_wassys', self.SOG*np.cos(np.deg2rad(self.COG))-self.stromsn)
        
#e.g. label plot in 4 min intervals
#ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(interval = 4))
#do I need ax.autoscale_view() ? Don't know.
    def minutes_index(self):
        '''return an index array to acess exactly one field per minute.
    
        Unfortunately, the NX2 time intervals are not exactly separated by 1s,
        some values are double or missing. 
        This functions return an index array of those entries where the minute
        changes, i.e. the first entry within each minute.
        '''
        return np.hstack((np.array([True]),(self.minute[1:] != self.minute[0:-1])))

    def write_kml(self, filename):
        '''write a kml file from an NX2 object

        Parameters
        ----------
        filename : string
            file name or path for output
        '''            
        with open(filename, 'w') as kmlFile:
            kmlFile.write(r'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
  <Document>''')
            kmlFile.write('  <name> Fahrtstrecke {0:2n}.{1:2n}.{2:2n} </name>'.format(*self.read_date))
            kmlFile.write(r'''  <description>Dies stellt die Fahrtstrecke der Galeere am angegebenen Tag dar. Sie sieht eckig aus, weil das GPS nur auf einige Meter genau ist. Ruder und Segelstrecken werden mit unterschiedlichen Farben angezeigt. Jede Strecke kann auf der Karte einzeln an- und ausgeschaltet werden. Bei jeder Strecke ist die Startzeit vermerkt.
Fragen an: Moritz.guenther@hs.uni-hamburg.de</description>
    <Style id="yellowLine">
      <LineStyle>
        <color>7f00ffff</color>
        <width>4</width>
      </LineStyle>
    </Style>
    <Style id="redLine">
      <LineStyle>
        <color>7f0000ff</color>
        <width>4</width>
      </LineStyle>
    </Style>''')
            if 'sailing' in self.keys():
                kmlFile.write(r'''    <Folder>
        <name>Ruderstrecke</name>
      <description>Hier war das Segel nicht gesetzt, entweder wurde gerudert oder Pause gemacht.</description>
      <open>0</open>  ''')
                phases = [list(g) for key, g in itertools.groupby(np.arange(len(self)), lambda k: (self.sailing[k] == 1.)) if key == False]
                for phase in phases: write_leg(self, kmlFile, phase, name ='Ruderstrecke', style = '#yellowLine', skip = 1)
                kmlFile.write('    </Folder>')
                kmlFile.write('    <Folder>')
                kmlFile.write('        <name>Segelstrecke</name>')
                kmlFile.write('      <description>Segel gesetzt!</description>') 
                kmlFile.write('      <open>0</open>  ')
                phases = [list(g) for key, g in itertools.groupby(np.arange(len(self)), lambda k: (self.sailing[k] == 1.)) if key == True]
                for phase in phases: write_leg(self, kmlFile, phase, name ='Segelstrecke', style = '#redLine', skip = 1)
                kmlFile.write('    </Folder>')
            else:
                write_leg(self, kmlFile, np.arange(len(self)), style = '#yellowLine')
            kmlFile.write('  </Document>')
            kmlFile.write('</kml>')
        print 'Wrote kml file: '+filename

def test(x,y):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S', tz=None))
        row = ax.bar(x,y, label='Ruderschläge', width=1./24./60.)
        xlab = ax.get_xticklabels()
        for label in xlab: label.set_rotation(30)
        import pdb
        pdb.set_trace()
        
