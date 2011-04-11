import NX2
#dat = NX2.NX2Table('../data/18tue_firstday.00.csv', (18,5,2009))
dat = NX2.NX2Table('../2008/080424eleventhday_sail.00.csv', (24,4,2008))
dat.add_rowing_old_format('../2008/Ruderschlaege.csv')
dat.plot_speeds()
dat.write_kml('/data/hguenther/Dropbox/Public/test1.kml')
