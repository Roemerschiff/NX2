import sys
import glob
import os
import os.path

import NX2

db_path = '/home/moritz/'
sys.path.append(db_path + 'Dropbox/code/python/NX2')


datapath = db_path + 'Dropbox/NX2/'
plotpath = db_path + 'Dropbox/NX2/2012/plots/'

dat = NX2.NX2Table(datapath + '2012/20120515_second_day_with_mast+rah.00.csv', (15,5,2012))
dat2 = NX2.NX2Table(datapath + '2012/20120515_second_day_with_mast+rah2.00.csv', (15,5,2012))
dat3 = NX2.NX2Table(datapath + '2012/20120516_third_day_with_mast+rah.00.csv', (16,5,2012))
dat4 = NX2.NX2Table(datapath + '2012/20120517_fourth_day_with_mast+rah.00.csv', (17,5,2012))
dat5 = NX2.NX2Table(datapath + '2012/20120517_fourth_day_with_mast+rah2.00.csv', (17,5,2012))
dat6 = NX2.NX2Table(datapath + '2012/20120518_fifth_day_with_mast+rah.00.csv', (18,5,2012))

dat.add_rowing_old_format(datapath + '/2012/Ruderschlaege2012.csv')
dat2.add_rowing_old_format(datapath + '/2012/Ruderschlaege2012.csv')
dat3.add_rowing_old_format(datapath + '/2012/Ruderschlaege2012.csv')
dat4.add_rowing_old_format(datapath + '/2012/Ruderschlaege2012.csv')
dat5.add_rowing_old_format(datapath + '/2012/Ruderschlaege2012.csv')
dat6.add_rowing_old_format(datapath + '/2012/Ruderschlaege2012.csv')

dat.write_kml(datapath +  'homepage/source/kml/'+'20120515_1.kml')
dat2.write_kml(datapath + 'homepage/source/kml/'+'20120515_2.kml')
dat3.write_kml(datapath + 'homepage/source/kml/'+'20120516_1.kml')
dat4.write_kml(datapath + 'homepage/source/kml/'+'20120517_1.kml')
dat5.write_kml(datapath + 'homepage/source/kml/'+'20120517_2.kml')
dat6.write_kml(datapath + 'homepage/source/kml/'+'20120518_1.kml')


merge = dat.where(np.ones(len(dat), dtype = bool))
merge2 = dat2.where(np.ones(len(dat2), dtype = bool))
merge3 = dat3.where(np.ones(len(dat3), dtype = bool))
merge4 = dat4.where(np.ones(len(dat4), dtype = bool))
merge5 = dat5.where(np.ones(len(dat5), dtype = bool))
merge6 = dat6.where(np.ones(len(dat6), dtype = bool))
merge.append(merge2)
merge.append(merge3)
merge.append(merge4)
merge.append(merge5)
merge.append(merge6)

# fit BSP to merged dataset
# now per hand
fit, con = merge.fit_BSP_corr()

plt.clf()
plt.plot(merge.SOG, merge.BSP, 'k.', label = 'alle')
plt.plot(merge.SOG[con], merge.BSP[con], 'r.', label = 'gefiltert')

plt.plot([0, plt.xlim()[1]], [0, fit.beta * plt.xlim()[1]],'b', lw = 3, label = 'Fit')

plt.legend(loc = 'upper left', numpoints=1)
#plt.text(8, 3, 'Steigung')
#plt.text(8, 2.5, '{0:4.2f}'.format(fit.beta[0]), color = 'b')
plt.xlabel('Geschwindigkeit: GPS')
plt.ylabel('Geschwindigkeit: Log')
plt.title(r'Bestimmung eines Korrekturfaktors: Mai 2012')

plt.savefig(plotpath + 'BSPcorr.png')


dat.BSP = dat.BSP / fit.beta[0]
dat2.BSP = dat2.BSP / fit.beta[0]
dat3.BSP = dat3.BSP / fit.beta[0]
dat4.BSP = dat4.BSP / fit.beta[0]
dat5.BSP = dat5.BSP / fit.beta[0]
dat6.BSP = dat6.BSP / fit.beta[0]
merge.BSP = merge.BSP / fit.beta[0]


fig = dat6.plot_speeds(t1=(10,24,00), t2=(10,38,59))

axs = fig.get_axes()
axs[0].legend(loc = 'lower left')
axs[1].legend(loc = 'upp right')
plt.draw()
plt.savefig(plotpath + 'Kalibrationsfahrt.png')
    


# require almost const speed
smoothedBSP = NX2.smooth_gauss(merge.BSP, 3.)
smoothedTWA = NX2.smooth_gauss(np.abs(merge.TWA), 3.)
smoothedTWS = NX2.smooth_gauss(merge.TWS, 3.)
index = (abs(np.diff(smoothedTWS)) < 0.01) # careful! n-1 elements! see below
# index = np.hstack((index, [False]))
fig, polar = plot_polar(smoothedTWA[index], smoothedTWS[index], smoothedBSP[index])


def plot_polar(angle, wind, bsp, fct = np.median):
    fig = plt.figure()
    fig.canvas.set_window_title('Polardiagramm')
    ax = fig.add_subplot(111, polar = True)
    color = ['r', 'g', 'b', 'y', 'k', 'c', 'orange']
    speedbins = np.array([0.,2.,4.,6.,8.,10.,12.])
    #make bins slightly larger than 15., so that 180. is part of last bin
    anglebins = np.arange(0., 181., 15.001)
    digspeed = np.digitize(wind, speedbins)
    digangle = np.digitize(np.abs(angle),anglebins)
    polar = np.zeros([len(speedbins)+1, len(anglebins)])
    for i in np.arange(1, len(twsbins)):
        for j in np.arange(1, len(anglebins)):
            polar[i,j] = fct(bsp[(digspeed==i) & (digangle==j)])
        ax.plot(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), polar[i,1:], color = color[i], lw = 3, label='{0:3.1f}-{1:3.1f} kn'.format(speedbins[i-1], speedbins[i]))
    ax.legend(loc='lower left')
    return fig, polar




dat3.remove_columns('rowpermin')
fig = dat3.plot_speeds()
axs = fig.get_axes()
axs[0].legend(loc = 'upper left')
axs[1].legend(loc = 'upper right')
plt.draw()
plt.savefig(plotpath + 'speeds3.png')


# fit, con = dat.fit_BSP_corr()
# fit2, con2 = dat2.fit_BSP_corr()
#
# plt.clf()
# plt.plot(dat.SOG[con], dat.BSP[con], 'r.', label = '1. Fahrt')
# plt.plot(dat2.SOG[con2], dat2.BSP[con2], 'b.', label = '2. Fahrt')
#
# plt.plot([0, plt.xlim()[1]], [0, fit.beta * plt.xlim()[1]],'b', lw = 3, label = 'Fit 1. Tag')
# plt.plot([0, plt.xlim()[1]], [0, fit2.beta * plt.xlim()[1]],'orange', lw = 3, label = 'Fit 2. Tag')
# plt.legend(loc = 'upper left')
# plt.text(8, 3, 'Steigung')
# plt.text(8, 2.5, '{0:4.2f}'.format(fit.beta[0]), color = 'b')
# plt.text(8, 2.0, '{0:4.2f}'.format(fit2.beta[0]), color = 'orange')
# plt.xlabel('Geschwindigkeit: GPS')
# plt.ylabel('Geschwindigkeit: Log')
# plt.title(r'Bestimmung eines Korrekturfaktors')
# plt.savefig(plotpath + 'BSPcorr.png')
