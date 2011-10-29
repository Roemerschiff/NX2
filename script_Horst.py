import NX2

dat18 = NX2.NX2Table('../2010/18tue_firstday.00.csv', (18,6,2010))
dat19 = NX2.NX2Table('../2010/19wed_secondday.00.csv', (19,6,2010))
dat20 = NX2.NX2Table('../2010/20thu_thirdday.00.csv', (20,6,2010))
dat202 = NX2.NX2Table('../2010/20thu_thirdday_2.00.csv', (20,6,2010))

dat18.write_kml('../2010/18tue_firstday.00.kml')
dat19.write_kml('../2010/19wed_secondday.00.kml')
dat20.write_kml('../2010/20thu_thirdday.00.kml')
dat202.write_kml('../2010/20thu_thirdday_2.00.kml')


H,xedges,yedges = np.histogram2d(abs(dat.TWA[sail]),dat.BSP[sail])
xtent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
plt.imshow(H, extent=xtent, interpolation='nearest',aspect='auto')

H, edges = np.histogramdd([np.abs(dat.TWA[sail]),dat.TWS[sail],dat.BSP[sail]])
plt.imshow(H[:,6,:], interpolation='nearest',aspect='auto')

#somehow make mean in BSP...
#operate only on subset of sail ..

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

plt.legend()