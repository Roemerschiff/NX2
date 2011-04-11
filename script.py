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

