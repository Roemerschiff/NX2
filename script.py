import NX2

dat = NX2.NX2Table('../2008/080424eleventhday_sail.00.csv', (24,4,2008))
dat.add_rowing_old_format('../2008/Ruderschlaege.csv')

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
    bsp[i,j] = np.mean(dat.BSP[(dat.sailing ==1)&(digtws==i+1)&(digtwa==j+1)])
  plt.polar(np.deg2rad(anglebins[0:-1]+np.diff(anglebins)/2.), bsp[i,:], label='v= {0:3.1f}'.format(twsbins[i:i+2].mean()))

plt.legend()




