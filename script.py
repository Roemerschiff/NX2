# -*- coding: utf-8 -*-
import glob
import os
from NX2.NX2 import NX2Table

## Input for Website
#make exclude Ruderschlare.csv etc. from csvlist
datapath = '/Users/hamogu/PersDropbox/NX2/'
csvlist = glob.glob(datapath + '2008/*_*.csv')

for fil in csvlist:
    datestr = os.path.basename(fil)
    dat = NX2Table(fil, (int(datestr[4:6]),int(datestr[2:4]),int(datestr[0:2])))
    dat.add_rowing_old_format(datapath + '2008/Ruderschlaege.csv')
    # dat.write_kml(fil + '.kml')
    dat.write_geojson('/Users/hamogu/code/NX2/docsandresults/source/years/'+os.path.basename(fil) + '.geojson')

csvlist = glob.glob(datapath + '2011/*_*_*_*.csv')

for fil in csvlist:
    datestr = os.path.basename(fil)
    dat = NX2Table(fil, (int(datestr[6:8]),int(datestr[4:6]),int(datestr[0:4])))
    dat.add_rowing_old_format(datapath + '2011/Ruderschlaege2011.csv')
    # dat.write_kml(fil + '.kml')
    dat.write_geojson('/Users/hamogu/code/NX2/docsandresults/source/years/'+os.path.basename(fil) + '.geojson')

csvlist = glob.glob(datapath + '2012/*_*_*_*.csv')

for fil in csvlist:
    datestr = os.path.basename(fil)
    dat = NX2Table(fil, (int(datestr[6:8]),int(datestr[4:6]),int(datestr[0:4])))
    dat.add_rowing_old_format(datapath + '2012/Ruderschlaege2012.csv')
    # dat.write_kml(fil + '.kml')
    dat.write_geojson('/Users/hamogu/code/NX2/docsandresults/source/years/'+os.path.basename(fil) + '.geojson')


import atpy
import asciitable
tab = atpy.Table(csvlist,type='ascii',Reader = asciitable.NoHeader)
tab.sort('col1')

for fil in tab.col1:
    datestr = os.path.basename(fil)
    date = (datestr[6:8],datestr[4:6],datestr[0:4])
    print '<P><A HREF="http://maps.google.de/maps?f=q&amp;hl=de&amp;geocode=&amp;q=http:%2F%2Fwww.hs.uni-hamburg.de%2FDE%2FIns%2FPer%2FGuenther%2FGaleere%2F'+datestr+'.kml&amp;ie=UTF8&amp;t=h&amp;z=15">Fahrt vom '+date[0]+'.'+date[1]+'.'+date[2]+'</A></P>'
# Replace + with %2B in html



https://github.com/hamogu/NX2/blob/master/docsandresults/source/years/geojson/080416thirdday_sail.00.csv.geojson
