# -*- coding: utf-8 -*-
import NX2

### Korrektur der BSP
dat = NX2.NX2Table(datapath+'/2011/20110504_third_day_with_mast+rah.00.csv', (4,5,2011))
d = dat.when(t1=(9,40,0),t2=(9,58,59))
d.plot_speeds()
plt.xlabel('Uhrzeit')
plt.ylabel('Geschwindigkeit [Knoten]')
plt.title('Geschwindigkeiten')
plt.legend(loc = 'center')
plt.savefig('../2011/plots/corr_BSP1.png')

ind = (d.BSP > 1.)
mean(d.SOG[ind]/d.BSP[ind])
#d.BSP = d.BSP * 1.145
fig = plt.figure()
fig.canvas.set_window_title('Bootsgeschwindigkeit')
ax = fig.add_subplot(111)
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M', tz=None))
sog = ax.plot(d.datetime(), d.SOG, label='GPS')
bsp = ax.plot(d.datetime(), d.BSP, label='Log - orginal')
bsp2 = ax.plot(d.datetime(), d.BSP * 1.145, label='Log - korrigiert')
xlab = ax.get_xticklabels()
for label in xlab: label.set_rotation(30)
plt.xlabel('Uhrzeit')
plt.ylabel('Geschwindigkeit [Knoten]')
plt.title('korrigierte Geschwindigkeiten')
plt.legend(loc = 'center')

annotate('Wende mit Streichen', xy=(d.datetime()[850], 1),  xycoords='data',
                xytext=(d.datetime()[750], 1.2), textcoords='data',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='right', verticalalignment='top',
                )
annotate('BSP zu niedrig zum Messen', xy=(d.datetime()[600], .1),  xycoords='data',
                xytext=(d.datetime()[600], .7), textcoords='data',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='center', verticalalignment='top',
                )
plt.savefig(plotpath + '/corr_BSP2.png')

### Ausgleiten und Aufstoppen
dat = NX2.NX2Table('../2011/20110505_fourth_day_with_mast+rah.00.csv', (5,5,2011))
d = dat.when(t1=(9,57,0),t2=(10,02,59))
d.BSP = d.BSP * 1.13
d.plot_speeds()
plt.xlabel('Uhrzeit')
plt.ylabel('Geschwindigkeit [Knoten]')
plt.title('Ausgleiten')
plt.legend(loc = 'top right')
annotate(r'zurueck treiben', xy=(d.datetime()[300], .7),  xycoords='data',
                xytext=(d.datetime()[300], 1.2), textcoords='data',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='center', verticalalignment='top',
                )

plt.savefig('../2011/plots/Ausgleiten.png')

dat = NX2.NX2Table('../2011/20110506_fifth_day_with_mast+rah_quer.00.csv', (6,5,2011))
d = dat.when(t1=(9,42,0),t2=(9,47,59))
d.BSP = d.BSP * 1.13
d.plot_speeds()
plt.xlabel('Uhrzeit')
plt.ylabel('Geschwindigkeit [Knoten]')
plt.title('Aufstoppen')
plt.legend(loc = 'top right')
text(d.datetime()[70], .7, 'Tempofahrt')
text(d.datetime()[170], 1.7, 'Aufstoppen')
text(d.datetime()[270], .7, 'Tempofahrt')
plt.savefig('../2011/plots/Aufstoppen.png')

### Polardiagramm
#import glob
#filelist = glob.glob('../2011/2011*csv')
#dat = NX2.NX2Table(filelist[0], (int(filelist[0][14:16]),int(filelist[0][12:14]),int(filelist[0][8:12])))
#for fil in filelist[1:]:
    #data = NX2.NX2Table(fil, (int(fil[14:16]),int(fil[12:14]),int(fil[8:12])))
    #dat.append(data)    

#dat.add_rowing_old_format('../2011/Ruderschlaege2011.csv')

#dat.BSP = dat.BPS * 1.13
### first simple polar diagram
# does not do filtering yet
# plot needs to be limited to only halfsphere
# TBD : make this into proper procedures
dat = merge.where(merge.LON > -500) # everywhere!

plt.clf()

twsbins = np.array([0.,2.,4.,6.,8.])
digtws = np.digitize(dat.TWS, twsbins)
#make bins slightly larger than 15., so that 180. is part of last bin
anglebins = np.arange(0., 181., 10.001)
digtwa = np.digitize(np.abs(dat.TWA),anglebins)
bsp = np.zeros([max(digtws),max(digtwa)])
for i in np.arange(1,len(twsbins)):
  for j in np.arange(1,len(anglebins)):
    bsp[i,j] = np.median(dat.BSP[(dat.sailing ==1)&(digtws==i)&(digtwa==j)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,1:], label='{0:3.1f} kn'.format(twsbins[i-1:i+1].mean()),resolution = 5)

plt.legend(loc = 4)
plt.title('Polardigramm')
plt.savefig(plotpath +'/Polardiagram_no_filter_full.png')



plt.clf()

twsbins = np.array([0.,2.,4.,6.,8.])
digtws = np.digitize(dat.TWS, twsbins)
#make bins slightly larger than 15., so that 180. is part of last bin
anglebins = np.arange(0., 181., 15.001)
digtwa = np.digitize(np.abs(dat.TWA),anglebins)
bsp = np.zeros([max(digtws),max(digtwa)])
for i in np.arange(1,len(twsbins)):
  for j in np.arange(1,len(anglebins)):
    bsp[i,j] = np.median(dat.BSP[(dat.sailing ==1)&(digtws==i)&(digtwa==j)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,1:], label='{0:3.1f} kn'.format(twsbins[i-1:i+1].mean()),resolution = 5)

plt.legend(loc = 4)
plt.title('Polardigramm')
plt.savefig(plotpath +'/Polardiagram_no_filter.png')


dat = merge.where(merge.LON < 500.)
dat.BSP = NX2.smooth_gauss(dat.BSP, 5.)
dat.TWS = NX2.smooth_gauss(dat.TWS, 5.)
dat.TWA = NX2.smooth_gauss(dat.TWA, 5.)
sailing = NX2.smooth_gauss(np.array(dat.sailing, dtype = np.float), 30.)

con3 = (abs(np.diff(dat.BSP)) < 0.05) # careful! n-1 elements!
myl = con3.tolist()
myl.append([True])
con3 = np.array(myl)

con2 = (abs(np.diff(dat.TWA)) < .5) # careful! n-1 elements!
myl = con2.tolist()
myl.append([True])
con2 = np.array(myl)

con1 = (abs(np.diff(dat.TWS)) < 0.05) # careful! n-1 elements!
myl = con1.tolist()
myl.append([True])
con1 = np.array(myl)

ind = con1 & con2 & con3
print(ind.sum(), con1.sum(), con2.sum(), con3.sum(), (ind & (merge.sailing > 0.98)).sum())



plt.clf()
twsbins = np.array([0.,2.,4.,6.,8.])
digtws = np.digitize(dat.TWS, twsbins)
#make bins slightly larger than 15., so that 180. is part of last bin
anglebins = np.arange(0., 181., 15.001)
digtwa = np.digitize(np.abs(dat.TWA),anglebins)
bsp = np.zeros([max(digtws),max(digtwa)])
for i in np.arange(1,len(twsbins)):
  for j in np.arange(1,len(anglebins)):
    bsp[i,j] = np.median(dat.BSP[(sailing >.99)&(digtws==i)&(digtwa==j)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,1:], label='{0:3.1f} kn'.format(twsbins[i-1:i+1].mean()),resolution = 5)


plt.legend(loc = 4)
plt.title('Polardigramm')
plt.savefig(plotpath +'/Polardiagram_filtered.png')


f = figure()
subplots_adjust(hspace=0.001)
subplots_adjust(vspace=0.001)
for i in range(len(anglebins)-1):
    for j in range(len(twsbins)-1):
        print i, j, len(anglebins)-1, len(twsbins)-1, i*len(twsbins)+j+1
        ax = subplot(len(anglebins)-1, len(twsbins)-1, i*(len(twsbins)-1)+j+1) 
        ind = (sailing >.99)&(digtws==j+1)&(digtwa==i+1)
        hist(dat.BSP[ind], range = (0,5))
        #if j== 0:
            #ax.title = '{0:3.1f}-{1:3.1f}'.format(twsbins[j], twsbins[j+1])
        if i == 0:
            ax.ytitle = '{0:3.1f}'.format(np.mean(anglebins[i:i+2]))
        if j!= (len(twsbins)-1):
            xticklabels = ax.get_xticklabels()
            setp(xticklabels, visible = False)
        if i != (len(anglebins)-1):
            yticklabels = ax.get_yticklabels()
            setp(yticklabels, visible = False)



ax1 = subplot(311)
ax1.plot(t,s1)
yticks(arange(-0.9, 1.0, 0.4))
ylim(-1,1)

ax2 = subplot(312, sharex=ax1)
ax2.plot(t,s2)
yticks(arange(0.1, 1.0,  0.2))
ylim(0,1)

ax3 = subplot(313, sharex=ax1)
ax3.plot(t,s3)
yticks(arange(-0.9, 1.0, 0.4))
ylim(-1,1)

xticklabels = ax1.get_xticklabels()+ax2.get_xticklabels()
setp(xticklabels, visible=False)

# Hochstgeschwindigkeit 2011 without Mast and Rah
import NX2
datapath = '/home/moritz/Dropbox/NX2/'
dat22 = NX2.NX2Table(datapath + '2011/20110522_fourteenth_day_without_mast+rah.00.csv', (22,05,2011))
dat22.add_rowing_old_format(datapath + '/2011/Ruderschlaege2011.csv')

fig = plt.figure()
fig.canvas.set_window_title('Bootsgeschwindigkeit')
ax = fig.add_subplot(111)
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M', tz=None))

ind = (dat22.time() >= datetime.time(10,39,00)) & (dat22.time() <= datetime.time(11,5,00))

sog = ax.plot(dat22.datetime()[ind], dat22.SOG[ind], label='SOG')
bsp = ax.plot(dat22.datetime()[ind], dat22.BSP[ind]/0.87, label='BSP')
ax.legend(loc = 'upper left')
xlab = ax.get_xticklabels()
for label in xlab: label.set_rotation(30)
lab = plt.ylabel('Geschwindigkeit in Knoten')
lab = plt.xlabel('Uhrzeit')
        
ax2 = ax.twinx()
index = dat22.minutes_index() & ind
minutes = np.array(map(lambda x: x.replace(second = 0, microsecond=0), dat22.datetime()[index]))
row = ax2.bar(minutes, dat22.rowpermin[index], label=u'Ruderschläge', width=1./24./60., linewidth = 0., alpha = 0.4, color='r')
ax2.set_ylabel(u'Ruderschläge', color='r')
ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M', tz=None))
for tl in ax2.get_yticklabels():
    tl.set_color('r') 

#ax2.legend()

