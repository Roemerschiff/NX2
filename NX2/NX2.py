# -*- coding: utf-8 -*-
import os
import datetime
import itertools
from warnings import warn
from exceptions import UserWarning

import numpy as np
import scipy
import scipy.interpolate
import scipy.odr
from scipy.io.idl import readsav
import matplotlib.pylab as plt
import matplotlib
import matplotlib.dates

import asciitable
import atpy

from . import math
from . import polar

mps2knots = 0.51444  # factor to convert m/s to knots

# Module level class and func for kml file support
class OriginError(Exception):
    pass
    
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


# here make the NX2data class

class NX2InterpolationWarning(UserWarning):
    '''Warning class for interpolation of data columns.
    '''
    def __init__(self, column, maxgap  = np.inf):
        self.column = column
        self.maxgap = maxgap

    def __str__(self):
        if self.maxgap == np.inf:
            return 'column '+ self.column + ' contains more than 2% nans. No automatic interpolation performed.' 
        else:
            return 'Interpolating over missing values in column {0}\nMaximum data gap is {1} lines.'.format(self.column, self.maxgap)

class NX2RowingWarning(UserWarning):
    '''Warning class for warning related to the matching of rowing data files.'''
    pass

#TBD: ideas for further development
#   read_NX2: define proper timezone instead of timeoffset

def read_NX2(self, filename, date, corr_bsp = 1.,origin = None, timeoffset = 2, verbose = True):
    '''read in csv data and initialize table
    
    Parameters
    ----------
    filename : string
        filename as string or other input compatible with asciitable
    date: tuple of integers ``(day, month, year)``
        date of measurement
    corr_bsp: float 
        multiplictive correction factor for BSP
    origin: tuple 
        (lat, lon) in deg of x,y origin
        default: lat, lon at first datapoint
    timeoffset: float
        hours to be added to convert UT to local
    '''
    include_names = ['TIME', 'LAT', 'LON', 'AWA', 'AWS', 'BSP', 'COG', 'DFT', 'HDC', 'SET', 'SOG', 'TWA', 'TWS']
    converters = {'TIME': asciitable.convert_list(float)}

    try:
        atpy.Table.__init__(self, filename, type='ascii', delimiter=',', fill_values=('','nan'), data_start = 5, include_names = include_names, guess = False)
        if verbose: print 'Reading new format NX2 table - Export with 1.08'
    except asciitable.InconsistentTableError:
        if verbose: print 'Reading NX2 table, which was exported with 1.05'
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
            warn('TIME contains > 2 % nans. Interpolating ...', NX2InterpolationWarning)
            self.fill_nans(name)
        else:
            warn(NX2InterpolationWarning(name)) 

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

def sec2hms(sec):
    h, rest = divmod(sec,3600)
    m, rest = divmod(rest, 60)
    s, rest = divmod(rest, 1)
    return h, m, s

class NX2Table(atpy.Table):
    '''Basic catalog object.
    '''
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            raise ValueError('Filename and date tuple required.')
        if len(args) > 1:
            kwargs['type'] = 'NX2'
        atpy.Table.__init__(self, *args, **kwargs)
    
    def datetime(self):
        '''Return an np.array of ``datetime.datetime`` object for each data point

        Useful for plotting, so matplotlib can label the x-axis correctly.
        '''
        return np.array(map(datetime.datetime, self.year, self.month, self.day, self.hour, self.minute, self.sec))

    def time(self):
        '''Return an np.array of ``datetime.time`` object for each data point

        Useful for plotting, so matplotlib can label the x-axis correctly.
        '''
        return np.array(map(datetime.time, self.hour, self.minute, self.sec))
    
    def fill_nans(self, column):
        index = np.isfinite(self[column])
        warn(NX2InterpolationWarning(column, max([len(list(v)) for g,v in itertools.groupby(index) if not g])))
        if column == 'TIME':
            x = np.arange(len(self),dtype = np.float)
            func = scipy.interpolate.interp1d(x[index],self[column][index], bounds_error = False)
            self[column][~index] = func(x[~index])
            timeints = np.asarray(self['TIME'], dtype = np.int)
            # cannot change dtype of col in place, so remove and add again
            # as int
            self.remove_columns('TIME')
            self.add_column('TIME', timeints, position = 0)
        else:
            func = scipy.interpolate.interp1d(self.TIME[index],self[column][index], bounds_error = False)
            self[column][~index] = func(self.TIME[~index])

    def where(self, mask):
        new_table = atpy.Table.where(self, mask)
        new_table.origin = self.origin
        new_table.read_date = self.read_date
        return new_table
        
    def when(self, t1=(0,0,0),t2=(23,59,59)):
        '''Select a subset of the table
        
        Parameters
        ----------
        t1, t2 : tuple
            Start and end time in the form ``(h, m, s)``
        '''
        ind = (self.time() >= datetime.time(*t1)) & (self.time() <= datetime.time(*t2))
        return self.where(ind)
    
    def fit_BSP_corr(self):
        '''fit a linear correlation between BSP and SOG
        
        Only points which fullfill the following criteria are used:
        
            - ``BSP > 0``
            - ``np.abs(COG-HDC) < 15``
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
        smoothed = math.smooth_gauss(self.BSP, 3.)
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
        '''Return an x/y overview plot of boat path, wind and speeds
        '''
        fig = plt.figure()
        fig.canvas.set_window_title('Kurs und Windrichtung')
        ax = fig.add_subplot(111)
        ax.plot(self.x, self.y,'k')
        # overplot path with saling in blue
        if 'sailing' in self.keys():
            # make groups of indices with the sail up
            for sail, ind in itertools.groupby(range(len(self)), key = lambda a:self.sailing[a]):
                if sail ==1 :
                  index = list(ind)
                  ax.plot(self.x[index], self.y[index],'b')
        wind_v = self.TWS / mps2knots
        wind_ang = self.TWA + self.HDC + 180.
        quiver_wind = ax.quiver(self.x[::n],self.y[::n], self.TWS[::n]*np.sin(wind_ang[::n]/180.*np.pi), self.TWS[::n]*np.cos(wind_ang[::n]/180.*np.pi), scale = scale, color= 'g')
        quiver_bsp  = ax.quiver(self.x[::n],self.y[::n], self.BSP[::n]*np.sin(self.HDC[::n]/180.*np.pi), self.BSP[::n]*np.cos(self.HDC[::n]/180.*np.pi), scale = scale)
        quiver_sog  = ax.quiver(self.x[::n],self.y[::n], self.SOG[::n]*np.sin(self.COG[::n]/180.*np.pi), self.SOG[::n]*np.cos(self.COG[::n]/180.*np.pi), scale = scale, color= 'b')
        if scale == None:
            qk_scale = None
        else:
            qk_scale = scale/20.
        qk_wind = ax.quiverkey(quiver_wind, .1, 0.95, qk_scale, 'Wind', labelpos='E')
        qk_bsp = ax.quiverkey(quiver_bsp, .1, 0.9, qk_scale, 'Fahrt im Wasser (ohne Drift)', labelpos='E')
        qk_sog = ax.quiverkey(quiver_sog, .1, 0.85, qk_scale, u'Bewegung über Grund', labelpos='E')
        ax.set_xlabel('West - Ost [Meter]')
        ax.set_ylabel(u'Süd - Nord [Meter]')
        return fig
        
    def plot_speeds(self, t1=(0,0,0),t2=(23,59,59)):
        '''Return a figure that shows BSP, SOG and rowing (if posible)
        '''
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
 
    def plot_polar(self, fct = np.median, speedbins = np.array([0.,2.,4.,6.,8.,10.,12.]), anglebins = np.arange(0., 181., 15.001), color = ['r', 'g', 'b', 'y', 'k', 'c', 'orange']):
        '''Return a polar plot'''
        polardata  = polar.group(self.TWA, self.TWS, self.BSP, speedbins, anglebins, fct=fct)
        fig = plt.figure()
        fig.canvas.set_window_title('Polardiagramm')
        aux, ax_original = polar.setup_plot(fig, 111)
        polar.plot(aux, polardata, speedbins, anglebins)
        
        return fig
    
        
    def add_rowing_old_format(self, filename, verbose = True):
        '''add rowing and sailing data
        
        :input: filename for cvs file in format as used in 2008
        '''
        if verbose: print 'Input data does not contain info on month and year.'
        rowdata = atpy.Table(filename, type = 'ascii', delimiter = ';')
        #rowtime = np.array(map(lambda x: datetime.datetime(self.read_date[2],self.read_date[1],*x), zip(rowdata['Tag'], rowdata['Stunde'], rowdata['Minute'])))
        if 'Ruderschlaege/Minute' in rowdata.keys():
            if verbose: print 'Load rowing data'
            if 'rowpermin' in self.keys():
                warn('Overwriting rowing data', NX2RowingWarning)
            else:    
                self.add_empty_column('rowpermin', dtype = '<i4', null = 0)
        if 'Segel' in rowdata.keys():
            if verbose: print 'Load sailing data'
            if 'sailing' in self.keys():
                wanr('Overwriting sailing data', NX2RowingWarning)
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

    def write_kml(self, filename, verbose = True):
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
        if verbose: print 'Wrote kml file: '+filename        

def remove_Danube_current(data):
    '''read Danube current simulation and transform data basis system

    This procedure read a current simulation of the Danube current in the
    region north of Regensburg, where the Navis Lusoria was tested in 2006.
    It adds 2 columns to the NX2 table, that contain the current in the x,y
    coordinate system (measured west-> east and south-> north) at each 
    position of the ship.
    Then, the speed over ground (contained in SOG and COG) is transformed into
    a coordinate system that moves with the water. Thus, after this procedure, 
    the SOG is not longer the "speed over ground", but instead the "speed over 
    flowing river" and the COG is the "course over flowing river"! Similarly,
    the TWS and the TWA are transformed ino the same coortinate system of the
    flowing river.

    The purpose of this is to correct SOG, COG, TWS and TWA in such a way
    that the usual procedures for plotting the polar diagram and the drift are
    applicable.

    Parameters
    ----------
    data : NX2Table
        The dataset to be modified
    '''
    if np.abs(data.origin[0]-49.0164) > 0.0001:
        raise OriginError('Lattitude of origin does not match origin of Schwaller data')
    if np.abs(data.origin[1]-12.0285) > 0.0001:
        raise OriginError('Longitude of origin does not match origin of Schwaller data')      
        
    schwaller = readsav(os.path.join(os.path.dirname(__file__), 'data', 'stromgeschwindigkeit.sav'))['strom']
    xy = np.vstack((schwaller['X'][0],schwaller['Y'][0])).transpose()
    schwallervx = scipy.interpolate.NearestNDInterpolator(xy, schwaller['VX'][0])
    schwallervy = scipy.interpolate.NearestNDInterpolator(xy, schwaller['VY'][0])
    selfxy = np.vstack((data.x, data.y)).transpose()
    data.add_column('currentwo', schwallervx(selfxy)/mps2knots)
    data.add_column('currentsn', schwallervy(selfxy)/mps2knots)
    vx_wassys = data.SOG*np.sin(np.deg2rad(data.COG))-data.currentwo
    vy_wassys = data.SOG*np.cos(np.deg2rad(data.COG))-data.currentsn
    TWxwater = data.TWS*np.sin(np.deg2rad(data.TWA + data.HDC + 180.))-data.currentwo
    TWywater = data.TWS*np.cos(np.deg2rad(data.TWA + data.HDC + 180.))-data.currentsn
    data.SOG = np.sqrt(vx_wassys**2+vy_wassys**2)
    data.COG = np.rad2deg(np.arctan2(vx_wassys, vy_wassys))
    data.TWS = np.sqrt(TWxwater**2 + TWywater**2)
    data.TWA = np.rad2deg(np.arctan2(TWxwater, TWywater)) - data.HDC + 180.



