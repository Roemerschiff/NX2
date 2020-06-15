
import sys
import glob
import os
import os.path
import datetime
import matplotlib as mpl

sys.path.append('/home/moritz/Dropbox/code/python/NX2')
import NX2

mpl.rcParams['font.size']=16
mpl.rcParams['legend.fontsize']='large'


datapath = '/home/moritz/Dropbox/NX2/'
plotpath = '/home/moritz/Dropbox/NX2/2010/report/'

d18 = NX2.NX2Table(datapath + '2010/18tue_firstday.00.csv',  (18, 5 , 2010))
d18.add_empty_column('sailing', dtype = float)
# hardcode sailing times. That is faster than making rowperminfile
d18.sailing[(d18.time() >= datetime.time(11,37)) & (d18.time() <= datetime.time(11,45))] = 1.
d18.sailing[(d18.time() >= datetime.time(17,42)) & (d18.time() <= datetime.time(17,52))] = 1.

d19 = NX2.NX2Table(datapath + '2010/19wed_secondday.00.csv', (19, 5 , 2010))
d19.add_empty_column('sailing', dtype = float)
d19.sailing[(d19.time() >= datetime.time(13,6)) & (d19.time() <= datetime.time(14,32))] = 1.
d19.sailing[(d19.time() >= datetime.time(14,53)) & (d19.time() <= datetime.time(15,25))] = 1.
#make datset off all data
merge = d18.where(np.ones(len(d18), dtype = bool))
merge.remove_columns('TIME')
d19.remove_columns('TIME')
merge.append(d19)
#check cal
kal  = d18.when((17,13,00),(17,24,00))
# read-date is required for kml, but no automatically copied
kal.read_date = d18.read_date
kal.write_kml('/home/moritz/Dropbox/Public/Horst_kal.kml')

kal.plot_speeds()
plt.legend(loc = 'lower right')
plt.savefig(plotpath + 'rkal_speeds.png')


fit18, con18 = d18.fit_BSP_corr()
fit19, con19 = d19.fit_BSP_corr()
fit, con = merge.fit_BSP_corr()
fit.pprint()

plt.clf()
plt.plot(d19.SOG[con19], d19.BSP[con19], 'r.', label = '2. Tag')
plt.plot(d18.SOG[con18], d18.BSP[con18], 'b.', label = '1. Tag')

plt.plot([0, plt.xlim()[1]], [0, fit18.beta * plt.xlim()[1]],'b', lw = 3, label = 'Fit 1. Tag')
plt.plot([0, plt.xlim()[1]], [0, fit19.beta * plt.xlim()[1]],'orange', lw = 3, label = 'Fit 2. Tag')
plt.plot([0, plt.xlim()[1]], [0, fit.beta * plt.xlim()[1]],'g', lw = 3, label = 'Fit gemeinsam')
plt.legend(loc = 'upper left')
plt.text(8, 3, 'Steigung')
plt.text(8, 2.5, '{0:4.2f}'.format(fit18.beta[0]), color = 'b')
plt.text(8, 2.0, '{0:4.2f}'.format(fit19.beta[0]), color = 'orange')
plt.text(8, 1.5, '{0:4.2f}'.format(fit.beta[0]), color = 'g')
plt.xlabel('Geschwindigkeit: GPS')
plt.ylabel('Geschwindigkeit: Log')
plt.title(r'Bestimmung eines Korrekturfaktors')
plt.savefig(plotpath + 'BSPcorr.png')
# There are some problems...
# HUGE up and down on BSP in some cases (+- 1.5 knots), so my usual smoothing
# needs to be increased by an order of magnitude!
# But seems as if Post-Cal is OK on first day to 5%
# (find beta = 0.95)
# However, that's different on second day: beta = 0.77 ?!?

# The following plot illustrates the problem:
d19test = d19.when(t1=(14,43,00),t2=(15,43,00))
d19test.plot_speeds()
plt.legend(loc = 'lower right')
plt.savefig(plotpath + 'sppedjumps.png')

dat = merge
#Korrektur der BSP
dat.BSP = dat.BSP/0.95
plt.clf()
color = ['r', 'g', 'b', 'y', 'k', 'c', 'orange']
twsbins = np.array([0.,2.,4.,6.,8.,10.,12.])
digaws = np.digitize(dat.AWS, twsbins)
#make bins slightly larger than 15., so that 180. is part of last bin
anglebins = np.arange(0., 181., 15.001)
digawa = np.digitize(np.abs(dat.AWA),anglebins)
bsp = np.zeros([max(digaws)+1,max(digawa)+1])
for i in np.arange(1,len(twsbins)):
  for j in np.arange(1,len(anglebins)):
    bsp[i,j] = np.median(dat.BSP[(dat.sailing ==1)&(digaws==i)&(digawa==j)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,1:], color = color[i], lw = 3, label='{0:3.1f}-{1:3.1f} kn'.format(twsbins[i-1], twsbins[i]))

plt.legend(loc = 4)
plt.title('Polardigramm - scheinbarer Wind')
plt.savefig(plotpath +'/Polardiagram_AW.png')



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
twsbins = np.array([0.,2.,4.,6.,8.,10,12.])
digtws = np.digitize(dat.TWS, twsbins)
#make bins slightly larger than 15., so that 180. is part of last bin
anglebins = np.arange(0., 181., 15.001)
digtwa = np.digitize(np.abs(dat.TWA),anglebins)
bsp = np.zeros([max(digtws)+1,max(digtwa)+1])
for i in np.arange(1,len(twsbins)):
  for j in np.arange(1,len(anglebins)):
    bsp[i,j] = np.median(dat.BSP[(sailing >.99)&(digtws==i)&(digtwa==j)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,1:], label='{0:3.1f}-{1:3.1f} kn'.format(twsbins[i-1], twsbins[i] ))


plt.legend(loc = 4)
plt.title('Polardiagramm')
plt.savefig(plotpath +'/Polardiagram_filtered.png')

#Hallo Moritz,

#hier einmal der Versuch, gute Zeiten für das Polardiagramm fest zu machen. Dabei liegt die Zeit scheinbar 2 Stunden auseinander. NX2 zeigt TIMDAT 11:07 an, aber 13:07 steht im Log-Eintrag. Ich zitiere unten die Log-Einträge.
#Interessant ist, dass die Spannung variert. Ist der Motor an erreicht sie sehr schnell wieder 13,7 V. Ist der Motor aus fällt sie schnell ab und ist unter 13,4-13,6 V. --> Guter Indikator, um die Logeinträge zu verifizieren, dass der Motor wirklich aus ist!

#Das sind die interessanteren Einträge der drei Tage:

#18tue_firstday.nxb
#09:53:00 Motor an
#10:25:00 angelegt
#11:28:00 abgelegt
#11:37:00 Genua Segel gesetzt, Motor aus
#11:45:00 Motor an
#12:17:00 Motor aus
#12:30 :00 Motor an
#12:59:00 Anker geworfen, Pause
#17:04:00 Motor an
#17:13:00 Kalibrierung vorbereiten
#17:17:00 Hinfahrt geschafft (BSP 3,79 / HDC 244,2 / SOG 2,40 / COG 227,7)
#17:24:00 Rückfahrt geschafft (21% BSP korrigieren, COG 5,40 auf Rückweg)
#17:33:00 Großsegel vorbereiten
#17:42:00 Großsegel gesetzt, Motor aus
#17:52:00 Motor an
#17:56:00 Segel geborgen

#19wed_secondday.nxb
#09:15:00 Motor an
#09:42:00 HDC+5° = COG
#10:04:00 Großsegel gesetzt, Motor läuft aber weiterhin
#13:06:00 längere Segelstrecke
#14:32:00 Motor wieder an zum besseren navigieren
#14:53:00 Motor aus
#15:25:00 Großsegel einholen
#15:44:00 Genua gesetzt, aber Motor läuft weiter

#20thu_thirdday.nxb
#10:58:00 Genua gesetzt, Motor aus
#11:13:00 Motor an
#11:16:00 Genua geborgen

#20thu_thirdday_2.nxb
#16:01:00 Genau gesetzt, aber Motor an
#16:55:00 Motor gedrosselt. aber läuft noch


#Die Kalibierungsfahrt am ersten Tag zu verifizieren, kann nicht schaden. Zeit 17:17 (bzw. 15:17).
#An zweiten Tag gibt es eine längere Segelstrecke, die vermutlich die meisten Daten bringen wird. Es war allerdings sehr windig, ich weiß also nicht, ob das Log zwischendurch nicht angeströmt wurde.
#Der dritte Tag lohnt sich nicht.

#Anbei übrigens noch ein Bild eines chinesischen Bootes aus dem Maritimen Museum in der Nähe von Shanghai. Die NX2 Files hast Du doch selbst noch, oder?

#Gruß
#Chris
