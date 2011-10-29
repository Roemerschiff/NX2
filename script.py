# -*- coding: utf-8 -*-
import sys
import glob
import os
import os.path

sys.path.append('/home/moritz/Dropbox/code/python/NX2')
import NX2

datapath = '/home/moritz/Dropbox/NX2/'
plotpath = '/home/moritz/Dropbox/NX2/2011/plots/'

dat = NX2.NX2Table(datapath + '2008/080424eleventhday_sail.00.csv', (24,4,2008))
dat.add_rowing_old_format(datapath + '/2008/Ruderschlaege.csv')

dat = NX2.NX2Table(datapath + '2011/20110504_third_day_with_mast+rah.00.csv', (4,5,2011))
dat.add_rowing_old_format(datapath + '2011/Ruderschlaege2011.csv')

# get our diagnostic plots with
dat.plot_speeds()
# or
dat.plot_course()

# other helpful commands
dat.keys()
plt.clf()  # clear figure in interactive plotting
plt.plot(dat.TIME, dat.COG)

H,xedges,yedges = np.histogram2d(abs(dat.TWA[sail]),dat.BSP[sail])
xtent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
plt.imshow(H, extent=xtent, interpolation='nearest',aspect='auto')

H, edges = np.histogramdd([np.abs(dat.TWA[sail]),dat.TWS[sail],dat.BSP[sail]])
plt.imshow(H[:,6,:], interpolation='nearest',aspect='auto')

#somehow make mean in BSP...
#operate only on subset of sail .

plt.savefig(plotpath + 'BSPcorr.png')



csvlist = glob.glob(datapath + '2011/*_*_*_*.csv')
fitres = np.zeros((len(csvlist),))

for i, fil in enumerate(csvlist):
    datestr = os.path.basename(fil)
    dat = NX2.NX2Table(fil, (int(datestr[6:8]),int(datestr[4:6]),int(datestr[0:4])))
    fit = dat.fit_BSP_corr()
    fit.pprint()
    fitres[i] = fit.beta
    plt.draw()


### TEST BSP ###
#Hi Costa,

#hier alle Daten gemerged und wie folgt gefiltert:
#- HDC und COG unterscheiden sich weniger als 15 Grad (keine Drift)
#- dv/dt < 0.01 kn/sec (diese Bedingung ist notig, weil BSP und SOG unterschiedlich schnell reagieren auf Anderungen der Geschwindigkeit)
#- BSP > 0: Filtert all Werte heraus, die so langsam sind, dass das log nichts anzeigt

#Der fit ergibt eine Steigung von 0.87 +/- 0.01.
#Ich habe auch mit a x + b experimentiert, aber das gibt sehr ahnliche Ergebnisse. Die Unterschiede zwischen den einzelnen Tage sind nicht signifikant (Bei manchen Fahrten haben wir auch nur so wenig Werte, dass man da die Steigung nicht so genau bestimmen kann.)
#Das ist doch schon mal gut. Offensichtlich kommt es auf eine paar cm mehr oder weniger beim Einbau nicht an.

#Moritz

datestr = os.path.basename(csvlist[0])
merge = NX2.NX2Table(csvlist[0], (int(datestr[6:8]),int(datestr[4:6]),int(datestr[0:4])))
#merge.keep_columns(['BSP', 'SOG', 'COG', 'HDC']) #keep object small
merge.remove_columns('TIME')
for fil in csvlist[1:]:
    datestr = os.path.basename(fil)
    dat = NX2.NX2Table(fil, (int(datestr[6:8]),int(datestr[4:6]),int(datestr[0:4])))
    dat.remove_columns(['TIME'])
    #dat.keep_columns(['BSP', 'SOG', 'COG', 'HDC'])
    merge.append(dat)

merge.add_rowing_old_format(datapath + '2011/Ruderschlaege2011.csv')
fit, con = merge.fit_BSP_corr()
fit.pprint()

ind = con & ~((merge.SOG < 1.5) & (merge.BSP > 2.))
plt.clf()
plt.plot(merge.SOG[ind], merge.BSP[ind], 'b.')
plt.plot([0, plt.xlim()[1]], [0, fit.beta * plt.xlim()[1]],'r', lw = 3)
plt.xlabel('Geschwindigkeit: GPS')
plt.ylabel('Geschwindigkeit: Log')
plt.title(r'Bestimmung eines Korrekturfaktors')
plt.savefig(plotpath + 'BSPcorr.png')


merge.BSP = merge.BSP / fit.beta[0]



## from here in in plots.py

## Input for Website
#make exclude Ruderschlare.csv etc. from csvlist
csvlist = glob.glob(datapath + '2011/*_*_*_*.csv')

for fil in csvlist:
    datestr = os.path.basename(fil)
    dat = NX2.NX2Table(fil, (int(datestr[6:8]),int(datestr[4:6]),int(datestr[0:4])))
    dat.add_rowing_old_format(datapath + '2011/Ruderschlaege2011.csv')
    dat.write_kml(fil + '.kml')

import atpy
import asciitable
tab = atpy.Table(csvlist,type='ascii',Reader = asciitable.NoHeader)
tab.sort('col1')

for fil in tab.col1:
    datestr = os.path.basename(fil)
    date = (datestr[6:8],datestr[4:6],datestr[0:4])
    print '<P><A HREF="http://maps.google.de/maps?f=q&amp;hl=de&amp;geocode=&amp;q=http:%2F%2Fwww.hs.uni-hamburg.de%2FDE%2FIns%2FPer%2FGuenther%2FGaleere%2F'+datestr+'.kml&amp;ie=UTF8&amp;t=h&amp;z=15">Fahrt vom '+date[0]+'.'+date[1]+'.'+date[2]+'</A></P>'
# Replace + with %2B in html


# Quick and dirty polar diagram

#twsbins = np.array([0.,2.,4.,6.,8.])
#digtws = np.digitize(dat.TWS, twsbins)
##make bins slightly larger than 15., so that 180. is part of last bin
#anglebins = np.arange(0., 181., 15.001)
#digtwa = np.digitize(np.abs(dat.TWA),anglebins)
#bsp = np.zeros([max(digtws),max(digtwa)])
#for i in range(max(digtws)):
  #for j in range(max(digtwa)):
    #bsp[i,j] = np.median(dat.BSP[(dat.sailing ==1)&(digtws==i+1)&(digtwa==j+1)])
  #plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,:-1], label='v= {0:3.1f}'.format(twsbins[i:i+2].mean()))
