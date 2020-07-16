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


def add_sailing_format(df, filename):
    sailing = pd.read_csv(filename,
                          parse_dates=[['date', 'setzen'], ['date', 'hoch']])
    for c in ['setzen', 'hoch']:
        sailing[c] = pd.to_datetime(sailing[f'date_{c}'],
                                    format='%Y:%m:%d %H:%M:%S')
        sailing[c] = sailing[c].dt.tz_localize(tz='Europe/Berlin')
    for row in sailing.iterrows():
        try:
            df.loc[row[1]['setzen']: row[1]['hoch'], 'Segel'] = 1
            df.loc[row[1]['setzen']: row[1]['hoch'], 'Ruderschlaege/Minute'] = row[1]['riemen'] * 20
        except KeyError:
            # This row has a time not covered in df
            pass
    return df


supporting_data = {'Ruderschlaege.csv': add_rowing_old_format,
                   'sailing.csv': add_sailing_format,
                   }


def wrap_pi(x):
    '''Wrap angle in range [-180, 180]

    Parameters
    ----------
    x: np.array
        angle in degrees

    Returns
    -------
    out : float
        angle in the range [-180,180]
    '''
    return x - 360 * np.floor((x + 180) / 360)


def default_and_smooth(df, columns=['TWA', 'TWS', 'absTWA',
                                    'bearingdiff',
                                    'TWA_drift', 'absTWA_drift'],
                       rollingtime=240,
                       **kwargs):
    '''Calculate some default derived values and smoothed columns'''
    # Useful derived columns
    if 'TWA' in df.columns:
        df['absTWA'] = np.abs(df['TWA'])
    if ('HDC' in df.columns) and ('COG' in df.columns):
        df['bearingdiff'] = wrap_pi(-(df['HDC'] - df['COG']))
        df['absbearingdiff'] = np.abs(df['bearingdiff'])
    if ('TWA' in df.columns) and ('bearingdiff' in df.columns):
        df['TWA_drift'] = wrap_pi(df['TWA'] - df['bearingdiff'])
        df['absTWA_drift'] = np.abs(df['TWA_drift'])
    if ('TWA' in df.columns) and ('HDC' in df.columns):
        # + 180, because TWA is measured "towards" the ship, e.g.
        # HDC = 0 and TWA = 0 means wind coming from N and
        # *pointing* south.
        df['windang'] = np.mod(df['HDC'] + df['TWA'] + 180., 360.)

    # Smoothing for existing columns
    for c in columns:
        if c in df.columns:
            df[c + '_s'] = df[c].ewm(**kwargs).mean()

    if 'Segel' in df.columns:
        df['Segel_s'] = df['Segel'].rolling(rollingtime, center=True).mean()
        # Pandas has only experimental support for masks, but deals well with nan.
        # For plotting purposes we make x/y columns with nan when the sail was not up.
        df['x_Segel_masked'] = df['x']
        df.loc[df['Segel'] != 1, 'x_Segel_masked'] = np.nan
        df['y_Segel_masked'] = df['y']
        df.loc[df['Segel'] != 1, 'y_Segel_masked'] = np.nan
    if 'Ruderschlaege/Minute' in df.columns:
        df['row_s'] = df['Ruderschlaege/Minute'].rolling(rollingtime,
                                                         center=True).mean()


def read_NX2(filename, corr_bsp=1, origin=None):
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
    df['time'] = pd.Timestamp(**date_from_filename(filename), tz='UTC')
    df['time'] = df['time'] + pd.to_timedelta(df['TIME'], unit='S')
    df['time'] = df['time'].dt.tz_convert('Europe/Berlin')
    df.set_index('time', inplace=True, drop=False)
    df.drop(['TIME'], axis=1)

    if ((np.abs(df.attrs['origin'][0] - 49.0164) < 0.0001) and
        (np.abs(df.attrs['origin'][1] - 12.0285) < 0.0001)):
            remove_danube_current(df)

    for filen, reader in supporting_data.items():
        f = os.path.join(os.path.dirname(filename), filen)
        if os.path.exists(f):
            df = reader(df, f)
            df.set_index('time', inplace=True, drop=False)
            # Replace nan with 0
            # nan is default value, but if we read sailing data
            # that means that the data net set to a number
            # means no sailing happend
            if 'Segel' in df.columns:
                df.loc[np.isnan(df['Segel']), 'Segel'] = 0
            break

    if 'BSP' in df.columns:
        df['BSP'] *= corr_bsp

    default_and_smooth(df, halflife=10)
    return df
