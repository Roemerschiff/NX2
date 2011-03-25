# -*- coding: utf-8 -*-
import asciitable
import numpy as np
import atpy
import datetime
import itertools
import scipy
import scipy.interpolate
import matplotlib.pylab as plt
import warnings
import matplotlib
import matplotlib.dates

mps2knots = 0.51444  # factor to convert m/s to knots

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
    #30 header values, but only 29 table entries, manually delete the last header value
    names = ['DATE', 'TIME', 'LAT', 'LON', 'AWA', 'AWS', 'BOD', 'BSP', 'BTW', 'CMG', 'COG', 'CTS', 'DEP', 'DFT', 'DMG', 'DST', 'DTW', 'HDC', 'LOG', 'RDR', 'SET', 'SOG', 'TBS', 'TEMP', 'TWA', 'TWS', 'VAR', 'VMG', 'WCV']
    
    atpy.Table.__init__(self, filename, type='ascii', delimiter=',', names=names, fill_values=('','nan'))
    
    self.read_date=date
    if origin: 
        self.origin = origin
    else:    
        self.origin = (self.LAT[0], self.LON[0])
    
    # TBD: self.TIME has non-unique entries
    # change [1,1,1] -> [1,1.33,1.66] ? Needs sub-s times then
    TIME = timeoffset * 3600 + self.TIME
    self.datetime = np.array(map(lambda x:datetime.datetime(date[2],date[1],date[0], *sec2hms(x)),TIME))
    self.time = np.array(map(lambda x:datetime.time(*sec2hms(x)),TIME))
    # remove all columns which contain only NaNs
    # interpolate nans in those columns with only a few nans
    for name in self.names:
        valid = np.isfinite(self[name])
        if valid.all():
            pass
        elif (~valid).all():
            self.remove_columns(name)
        elif (np.sum(valid)/ len(valid)) <= 0.98:
            self.fill_nans(name)
        else:
            print 'Warning: column '+ name + ' contains more than 2% nans. No automatic interpolation performed.'  

    r_earth=6300e3  #in Si unit - meter
    self.add_column('y', 2.*np.pi*r_earth/360.*(self.LAT-self.origin[0]))
    self.add_column('x', 2.*np.pi*r_earth*np.cos(self.LAT/180.*np.pi)/360.*(self.LON-self.origin[1]))

    self.BSP = self.BSP * corr_bsp

atpy.register_reader('nx2', read_NX2, override = True)

def sec2hms(sec):
    h, rest = divmod(sec,3600)
    m, rest = divmod(rest, 60)
    s, rest = divmod(rest, 1)
    return h, m, s

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
    
            
    
    def fill_nans(self, column):
        index = np.isfinite(self[column])
        print "Interpolating over missing values in column " + column + ':'
        print "Maximum data gap is ", str(max(len(list(v)) for g,v in itertools.groupby(self[column]))), 'seconds'
        func = scipy.interpolate.interp1d(self.TIME[index],self[column][index])
        self[column][~index] = func(self.TIME[~index])

    def where(self, mask):
        new_table = atpy.Table.where(self, mask)
        new_table.time = self.time[mask]
        new_table.origin = self.origin
        new_table.read_date = self.read_date
        return new_table

    def plot_course(self, scale = 50, n = 300):
        plt.clf()
        plt.plot(self.x, self.y,'k')
        # overplot path with saling in blue
        if 'sailing' in self.keys():
            # make groups of indices with the sail up
            for sail, ind in itertools.groupby(range(len(self)),key = lambda a:self.sailing[a]):
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
  
    def plot_speeds(self, t1=(0,0,0),t2=(23,59,59)):
        fig = plt.figure()
        fig.canvas.set_window_title('Bootsgeschwindigkeit')
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M', tz=None))
        #plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

        ind = (self.time >= datetime.time(*t1)) & (self.time <= datetime.time(*t2))

        sog = ax.plot(self.datetime[ind], self.SOG[ind], label='SOG')
        bsp = ax.plot(self.datetime[ind], self.BSP[ind], label='BSP')
        xlab = ax.get_xticklabels()
        for label in xlab: label.set_rotation(30)
        #plt.xticks(rotation=45)
        if 'rowpermin' in self.keys():
            ax2 = ax.twinx()
            index = self.minutes_index() & ind
            minutes = np.array(map(lambda x: x.replace(second = 0, microsecond=0),self.datetime[index]))
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
        rowtime = np.array(map(lambda x: datetime.datetime(self.read_date[2],self.read_date[1],*x), zip(rowdata['Tag'], rowdata['Stunde'], rowdata['Minute'])))
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
            ind = (self.datetime >= rowtime[i]) & (self.datetime <= (rowtime[i] + datetime.timedelta(0,60)))
            if 'rowpermin' in self.keys():
                self.rowpermin[ind] = rowdata['Ruderschlaege/Minute'][i]
            if 'sailing' in self.keys():
                self.sailing[ind] = rowdata['Segel'][i]
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
        minutes = np.array(map(lambda x: x.minute, self.datetime))
        return np.hstack((np.array([True]),(minutes[1:] != minutes[0:-1])))
# In [45]: scipy.signal.convolve(np.array([0.,0,0,1,0,0]),np.array([.5, .5,0.]),mode='same')
#Out[45]: array([ 0. ,  0. ,  0.5,  0.5,  0. ,  0. ])

def test(x,y):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S', tz=None))
        row = ax.bar(x,y, label='Ruderschläge', width=1./24./60.)
        xlab = ax.get_xticklabels()
        for label in xlab: label.set_rotation(30)
        import pdb
        pdb.set_trace()
        
