# -*- coding: utf-8 -*-
import NX2

### Korrektur der BSP
dat = NX2.NX2Table('../2011/20110504_third_day_with_mast+rah.00.csv', (4,5,2011))
d = dat.when(t1=(9,40,0),t2=(9,58,59))
d.plot_speeds()
plt.xlabel('Uhrzeit')
plt.ylabel('Geschwindigkeit [Knoten]')
plt.title('Geschwindigkeiten')
plt.legend(loc = 'center')
plt.savefig('../2011/plots/corr_BSP1.png')

ind = (d.BSP > 1.)
mean(d.SOG[ind]/d.BSP[ind])
d.BSP = d.BSP * 1.13
d.plot_speeds()
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
plt.savefig('../2011/plots/corr_BSP2.png')

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
import glob
filelist = glob.glob('../2011/2011*csv')
dat = NX2.NX2Table(filelist[0], (int(filelist[0][14:16]),int(filelist[0][12:14]),int(filelist[0][8:12])))
for fil in filelist[1:]:
    data = NX2.NX2Table(fil, (int(fil[14:16]),int(fil[12:14]),int(fil[8:12])))
    dat.append(data)    

dat.add_rowing_old_format('../2011/Ruderschlaege2011.csv')

dat.BSP = dat.BPS * 1.13
### first simple polar diagram
# does not do filtering yet
# plot needs to be limited to only halfsphere
# TBD : make this into proper procedures
plt.clf()

twsbins = np.array([0.,2.,4.,6.,8.])
digtws = np.digitize(dat.TWS, twsbins)
#make bins slightly larger than 15., so that 180. is part of last bin
anglebins = np.arange(0., 181., 15.001)
digtwa = np.digitize(np.abs(dat.TWA),anglebins)
bsp = np.zeros([max(digtws),max(digtwa)])
for i in range(max(digtws)):
  for j in range(max(digtwa)):
    bsp[i,j] = np.median(dat.BSP[(dat.sailing ==1)&(digtws==i+1)&(digtwa==j+1)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,:-1], label='v= {0:3.1f}'.format(twsbins[i:i+2].mean()))

plt.legend(loc = 4)
plt.title('Polardigramm')
plt.savefig('../2011/plots/Polardiagram.png')


