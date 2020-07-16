import os
import json
import itertools
import numpy as np
import pandas as pd


def _str2interval(s):
    '''Convert string into Pandas interval.

    Pandas saves Intervals as "(1.5, 4.5]".
    This function converts that string back into an interval.
    '''
    val1, val2 = s[1: -1].split(',')
    return pd.Interval(float(val1), float(val2))


def read_polar_csv(filename, col='BSP'):
    out = pd.read_csv(filename,
                      converters={'ang_bin': _str2interval,
                                  'v_bin': _str2interval})
    out.index = pd.MultiIndex.from_arrays([pd.Categorical(out['ang_bin']),
                                           pd.Categorical(out['v_bin'])],
                                          names=['ang_bin', 'v_bin'])
    return out.drop(columns=['ang_bin', 'v_bin'])[col].unstack()


def geojson(df, color={0: '#55AAFF', 1: '#00F', -1: '#F00'},
            descr={0: 'kein Segel', 1: 'Segel gesetzt', -1: 'Mastbruch'}):

    geoj = {"type": "FeatureCollection", "features": []}
    df = df.drop_duplicates(subset=['LAT', 'LON'])
    for name, grouped in df.groupby(df['Segel'].diff().abs().cumsum()):
        leg = {"type": "Feature", "geometry": {"type": "LineString"},
               "properties": {}}
        leg['properties']['description'] = descr[grouped['Segel'].median()]
        leg['properties']['stroke'] = color[grouped['Segel'].median()]
        leg['geometry']["coordinates"] = list(zip(grouped['LON'],
                                                  grouped['LAT']))
        leg['properties']['times'] = list(grouped.index.strftime('%Y-%m-%dT%H:%M:%S'))

        geoj['features'].append(leg)
    return geoj


# Note: Use gpxpy package instead?
def write_gpx(self, filename):
    from lxml import etree as ET

    root = ET.Element("gpx")
    trk = ET.SubElement(root, "trk")
    name = ET.SubElement(trk, "name").text = os.path.basename(filename).split('.')[0]
    lat  = self['LAT']
    lon = self['LON']
    t = self.datetime()
    for i in range(len(self)):
        trkpt = ET.SubElement(trk, "trkpt",
                              lat='{}'.format(lat[i]),
                              lon='{}'.format(lon[i]))
        tmp = ET.SubElement(trkpt, "time").text = t[i].astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        tree = ET.ElementTree(root)
        tree.write(filename, pretty_print=True)
