import numpy as np
import matplotlib.pyplot as plt

import NX2

def polar_grid(angle, wind, bsp, speedbins, anglebins, fig = None):
    '''Group data in bins according to wind angle and wind speed.

    Parameters
    ----------
    angle : np.ndarry
        Wind angles in degrees
    wind : np.ndarray
        wind speed in kn
    bsp : np.ndarray
        Boat speed in kn
    speedbins : ndarray
        bin boundaries for speed binning
    anglebins : ndarray
        bin boundaries for angle binning.
        Make sure that 180. is included in last bin and not on the boundary.
    fig : matplotlib.figure instance


    '''
    if fig is None:
        fig = plt.figure()

    if (angle.shape != wind.shape) or (angle.shape != bsp.shape):
        raise ValueError('angle, wind and bsp must have same number of elements')

    digspeed = np.digitize(wind, speedbins)
    digangle = np.digitize(np.abs(angle),anglebins)

    for i in np.arange(1, len(speedbins)):
        for j in np.arange(1, len(anglebins)):
            ax = fig.add_subplot(len(speedbins)-1, len(anglebins)-1, (i-1) * (len(anglebins)-1) + (j-1) + 1)
            ax.hist(bsp[(digspeed==i) & (digangle==j)].flatten(), range = [0,6], bins = 12)
            if j == 1:
                ax.set_ylabel('TWS:{0:1.0f}-{1:1.0f}'.format(speedbins[i-1], speedbins[i]))
            if i ==1:
                ax.set_title('{0:3.0f}-{1:3.0f} deg'.format(anglebins[j-1], anglebins[j]))

#polar_grid(d11.TWA, d11.TWS, d11.BSP, np.array([0.,2.,4.,6.,8.,10.,12.]), np.arange(0., 181., 15.001))

def sail(data):
    '''mark sailing only regions

    This function determines times with the sail up and no rowing.
    It also cut off the very beginning and end of each sailing phase,
    because in those times the sail was not set perfectly anyway.
    
    Parameters
    ----------
    data : NX2 data

    Returns
    -------
    sail : array of boolean
        True, if vessel was sailing AND not rowing.
    '''
    sail =  NX2.smooth_gauss(data['sailing'],20) > 0.99
    norow = np.abs(data['rowpermin']) < 0.01
    return sail & norow

def near_const(arr, max_diff = 0.01):
    '''mark regiosn with small gradiant in `arr`

    This is esssentially `abs(np.diff(arr)) < max_diff` with one element
    added, so that input and output have the same number of elements.

    Parameters
    ----------
    arr : 1-dim array
    max_diff : np.float
        maximum allowed gradiant between two elements
    
    '''
    con = abs(np.diff(arr)) < max_diff
    myl = con.tolist()
    myl.append([con[-1]])
    return np.array(myl)

#TWSs = NX2.smooth_expdec(d11['TWS'], 10)
