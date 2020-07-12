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


def read_polar_csv(filename):
    out = pd.read_csv(filename,
                      converters={'ang_bin': _str2interval,
                                  'v_bin': _str2interval})
    return out.pivot(index='ang_bin', columns='v_bin', values='BSP')


# Note: Use geojson package instead?
def write_geojson(self, filename):
    '''write geojson file from a NX2 object

    Parameters
    ----------
    filename : string
        file name or path for output
    '''
    geoj = {"type": "FeatureCollection", "features": []}
    for sail, group in itertools.groupby(np.arange(
            len(self)), lambda k: (self.sailing[k])):
        leg = {"type": "Feature", "geometry": {"type": "LineString"},
               "properties": {}}
        if sail == 1:
            leg['properties']['stroke'] = '#ffff00'
            leg['properties']['description'] = 'Segel gesetzt'
        elif sail == 0:
            leg['properties']['description'] = 'kein Segel'
            leg['properties']['stroke'] = '#ff0000'
        elif sail == -1:
            leg['properties']['description'] = 'Mastbruch'
            leg['properties']['stroke'] = '#00ff00'
        ind = [g for g in group]
        pos = np.vstack([self['LON'][ind], self['LAT'][ind]])
        # Remove dublicate entries, like those on mooring.
        ind = [0]
        for i in range(1, pos.shape[1]):
            if np.any(pos[:, i] != pos[:, i - 1]):
                ind.append(i)
        pos = pos[:, ind]

        leg['geometry']["coordinates"] = pos.T.tolist()

        geoj['features'].append(leg)

    with open(filename, 'w') as f:
        json.dump(geoj, f)


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
