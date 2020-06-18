import os
import json
import itertools
import numpy as np

from .polar import my_polar

csv_header = '''
# {}
#
# Unit: All speeds are in knots (Nautical mile / hour).
#       All angles are in degrees, 0 deg is "into the wind" and 180 deg means
#       "running downwind".
# Format:
# 2 D histrogram of averaged boat speeds
# The first two columns contain the lower and upper bin edge of each bin for
# the wind speed, the first two rows the lower and upper bin edge for the
# wind direction.
#
# Example:
# Look at the following table:
# nan nan 80
# nan nan 100
# 1 3 1.2
#
# This would mean that for wind speeds between 1 and 3 kn and beam reach
# (angle between 80 and 100 degrees) the boat made an average 1.2 kn.
'''


def write_polar_csv(filename, data, speedbins, anglebins,
                    title='Polar diagram', **kwargs):
    '''Write a polar diagram to a CSV file

    Parameters
    ----------
    filename : string
        filename
    data : np.array of space (N, M)
        data as 2D array
    speedbins : np.array
        Bis edges for speed histrogram
    anglebins:
        Bin edges for angles. Last bin should be inclusese of 180. deg
    title : string
    '''
    myp = my_polar(data, speedbins=speedbins, anglebins=anglebins, **kwargs)
    with open(filename, 'w') as f:
        f.write(csv_header.format(title))
        f.write('  nan   nan ' + ' '.join(['{:5.1f}'.format(a) for a in anglebins[:-1]]) + '\n')
        f.write('  nan   nan ' + ' '.join(['{:5.1f}'.format(a) for a in anglebins[1:]]) + '\n')
        for i in range(1, len(speedbins)):
            line = '{:5.2f} {:5.2f}'.format(speedbins[i - 1], speedbins[i])
            for j in range(1, len(anglebins)):
                line = line + ' {:5.2f}'.format(myp[i, j])
            f.write(line + '\n')


def read_polar_csv(filename):
    dat = np.loadtxt(filename)
    if not np.all(dat[0, 3:] == dat[1, 2:-1]):
        raise ValueError('Angle binning is non-continuous.')
    if not np.all(dat[3:, 0] == dat[2:-1, 1]):
        raise ValueError('TWS binning is non-continuous.')
    anglebins = np.zeros(dat.shape[1] - 1)
    speedbins = np.zeros(dat.shape[0] - 1)
    anglebins[:-1] = dat[0, 2:]
    anglebins[-1] = dat[1, -1]
    speedbins[:-1] = dat[2:, 0]
    speedbins[-1] = dat[-1, 1]
    return dat[2:, 2:], speedbins, anglebins


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
