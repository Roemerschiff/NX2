import os
import re
from glob import glob

import numpy as np
import pandas as pd

from scipy.io.idl import readsav
from scipy.interpolate import NearestNDInterpolator

r_earth = 6300e3
mps2knots = 0.51444  # factor to convert m/s to knots


def date_from_filename(filename):
    f = os.path.basename(filename)
    match = re.match('[0-9]+', f)
    if match:
        if match.end() == 6:
            year = 2000 + int(f[0:2])
            month = int(f[2:4])
            day = int(f[4:6])
        elif match.end() == 8:
            year = int(f[0:4])
            month = int(f[4:6])
            day = int(f[6:8])
        else:
            raise ValueError('Filename ' + f + ' must start with 6 or 8 digit date.')
    else:
        raise ValueError('Filename ' + f + ' does not start with the rowing date.')
    return {'day': day, 'month': month, 'year': year}


def remove_danube_current(df):
    '''read Danube current simulation and transform data basis system

    This procedure read a current simulation of the Danube current in the
    region north of Regensburg, where the Navis Lusoria was tested in 2006.
    It adds 2 columns to the NX2 table, that contain the current in the x,y
    coordinate system (measured west-> east and south-> north) at each
    position of the ship.
    Then, the speed over ground (contained in SOG and COG) is transformed into
    a coordinate system that moves with the water. Thus, after this procedure,
    the SOG is not longer the "speed over ground", but instead the "speed over
    flowing river" and the COG is the "course over flowing river"! Similarly,
    the TWS and the TWA are transformed ino the same coortinate system of the
    flowing river.

    The purpose of this is to correct SOG, COG, TWS and TWA in such a way
    that the usual procedures for plotting the polar diagram and the drift are
    applicable.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset to be modified
    '''
    schwaller = readsav(os.path.join(os.path.dirname(
        __file__), '..', 'data', '2006', 'stromgeschwindigkeit.sav'))['strom']
    xy = np.vstack((schwaller['X'][0], schwaller['Y'][0])).transpose()
    schwallervx = NearestNDInterpolator(xy, schwaller['VX'][0])
    schwallervy = NearestNDInterpolator(xy, schwaller['VY'][0])
    selfxy = np.vstack((df['x'], df['y'])).transpose()
    df['currentwo'] = schwallervx(selfxy) / mps2knots
    df['currentsn'] = schwallervy(selfxy) / mps2knots
    vx_wassys = df['SOG'] * np.sin(np.deg2rad(df['COG'])) - df['currentwo']
    vy_wassys = df['SOG'] * np.cos(np.deg2rad(df['COG'])) - df['currentsn']
    TWxwater = df['TWS'] * np.sin(np.deg2rad(df['TWA'] + df['HDC'] + 180.)) - df['currentwo']
    TWywater = df['TWS'] * np.cos(np.deg2rad(df['TWA'] + df['HDC'] + 180.)) - df['currentsn']
    df['SOG'] = np.sqrt(vx_wassys**2 + vy_wassys**2)
    df['COG'] = np.rad2deg(np.arctan2(vx_wassys, vy_wassys))
    df['TWS'] = np.sqrt(TWxwater**2 + TWywater**2)
    df['TWA'] = np.rad2deg(np.arctan2(TWxwater, TWywater)) - df['HDC'] + 180.


def add_rowing_old_format(df, filename):
    rowsail = pd.read_csv(filename, sep=';')
    df['Tag'] = df.index.day
    df['Stunde'] = df.index.hour
    df['Minute'] = df.index.minute
    newdf = pd.merge(df, rowsail, how='left')
    newdf.drop(['Tag', 'Stunde', 'Minute'], axis='columns')
    return newdf


def bearingdiff180(a, b):
    '''Calculate the smallest difference between two bearings.

    There are two complications here compared to the usual ``a-b``:

        - The angle wraps around at 360 deg.
        - A-priory it's not clear if the shortest difference between two
          bearings is clockwise or anti-clockwise.

    Parameters
    ----------
    a, b: np.float
        angles in degrees

    Returns
    -------
    out : float
        smallest difference between ``a`` and ``b`` in the range [-180,180]
    '''
    return np.mod((b - a) + 180. + 360., 360.) - 180.


def default_and_smooth(df, columns=['BSP', 'TWS', 'absTWA', 'bearingdiff'],
                       rollingtime=240,
                       **kwargs):
    '''Calculate some default derived and smoothed columns'''
    df['absTWA'] = np.abs(df['TWA'])
    if ('HDC' in df.columns) and ('COG' in df.columns):
        df['bearingdiff'] = np.abs(bearingdiff180(df['HDC'], df['COG']))
    for c in columns:
        df[c + '_s'] = df[c].ewm(**kwargs).mean()
    if 'Segel' in df.columns:
        df['Segel_s'] = df['Segel'].rolling(rollingtime, center=True).mean()
        # Pandas has only experimental support for masks, but deals with nan well.
        df['x_Segel_masked'] = df['x']
        df.loc[df['Segel'] != 1, 'x_Segel_masked'] = np.nan
    if 'Ruderschlaege/Minute' in df.columns:
        df['row_s'] = df['Ruderschlaege/Minute'].rolling(rollingtime,
                                                         center=True).mean()
    if ('bearingdiff' in df.columns) and ('absTWA_s' in df.columns):
        df['absTWA_drift_s'] = df['absTWA_s'] + df['bearingdiff']
    if ('TWA' in df.columns) and ('HDC' in df.columns):
        df['windang'] = df['TWA'] + df['HDC'] + 180.


def read_NX2(filename, corr_bsp=1, origin=None, timeoffset=2):
    '''read in csv data and initialize table

    Parameters
    ----------
    filename : string
        filename as string or other input compatible with asciitable
    corr_bsp: float
        multiplictive correction factor for BSP
    origin: tuple
        (lat, lon) in deg of x,y origin
        default: lat, lon at first datapoint
    timeoffset: float
        hours to be added to convert UT to local
    '''
    df = pd.read_csv(filename)
    df.dropna(axis='columns', how='all', inplace=True)
    if origin is None:
        origin = df['LAT'][0], df['LON'][0]
    df.attrs['origin'] = origin
    df.attrs['filename'] = filename
    df['y'] = 2. * np.pi * r_earth / 360. * (df['LAT'] - origin[0])
    df['x'] = 2. * np.pi * r_earth / 360. * \
              np.cos(np.deg2rad(df['LAT'])) * (df['LON'] - origin[1])

    for col in ['AWS', 'TWS']:
        if col in df.columns:
            df[col] = df[col] / mps2knots
    df.interpolate(columns='TIME')
    df['time'] = pd.Timestamp(**date_from_filename(filename), tz='Europe/Berlin')
    df['time'] = df['time'] + pd.to_timedelta(df['TIME'] + timeoffset * 3600,
                                              unit='S')
    df.set_index('time', inplace=True, drop=False)
    df.drop(['TIME'], axis=1)

    if ((np.abs(df.attrs['origin'][0] - 49.0164) < 0.0001) and
        (np.abs(df.attrs['origin'][1] - 12.0285) < 0.0001)):
            remove_danube_current(df)

    rowsailfile = os.path.join(os.path.dirname(filename), 'Ruderschlaege.csv')
    if os.path.exists(rowsailfile):
        df = add_rowing_old_format(df, rowsailfile)
        df.set_index('time', inplace=True, drop=False)

    if 'BSP' in df.columns:
        df['BSP'] *= corr_bsp

    default_and_smooth(df, halflife=10)
    return df
