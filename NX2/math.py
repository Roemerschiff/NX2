'''Module with a few mathematical definitions

This module collects a few simple, mathematical functions to treat
data smoothing or the handling of angles.
'''
import numpy as np
import scipy.stats
from scipy.signal import convolve

def smooth_expdec(data, t_e):
    '''smooth an array with an exponential decay

    Parameters
    ----------
    data : np.ndarray
        input array to be smoothed
    t_e : int
         decay timescale of expoential in number of bins
         (for NX2 data, i.e. seconds)

    Returns
    -------
    out : np.ndarray
        smoothed array
    '''
    kernel = np.zeros(2*3*t_e+1)
    kernel[3*t_e:-1] = np.exp(-np.arange(3*t_e, dtype=np.float)/t_e)
    kernel = kernel / kernel.sum()
    return np.convolve(data, kernel, 'same')

def smooth_gauss(data, width):
    '''smooth an array with a gauss

    Parameters
    ----------
    data : np.ndarray
        input array to be smoothed
    t_e : int
         decay timescale of exponential in number of bins
         (for NX2 data, i.e. seconds)

    Returns
    -------
    out : np.ndarray
        smoothed array
    '''
    norm = scipy.stats.norm(0.,width)
    kernel = norm.pdf(np.arange(-3.*width, 3.001*width))
    kernel = kernel / kernel.sum()
    return np.convolve(data, kernel, 'same')

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
    return np.mod((b-a) + 180. + 360., 360.) -180.
