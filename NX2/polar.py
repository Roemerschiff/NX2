'''Module for polar plots

This module collects all functions necessary for polar plots,
ranging from the gridding for angles and wind speeds into an array
(:func:`NX2.polar.grid`) to the plotting (:func:`NX2.polar.plot`).
This also includes some of the filters that are mainly used for polar
plots (e.g. :func:`NX2.polar.sail`).
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Affine2D
from mpl_toolkits.axisartist import floating_axes
from matplotlib.projections import PolarAxes
from mpl_toolkits.axisartist.grid_finder import MaxNLocator

from . import math


def grid(angle, wind, bsp, speedbins, anglebins, fig=None):
    '''Plot a grid of data in bins according to wind angle and wind speed.

    The makes a grid of plots showing the distribution of the BSP in each
    ``angle`` and ``wind`` bin.

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
        If ``None``, a new figure instance is created.
    '''
    if fig is None:
        fig = plt.figure()

    if (angle.shape != wind.shape) or (angle.shape != bsp.shape):
        raise ValueError('angle, wind and bsp must have same number of elements')

    digspeed = np.digitize(wind, speedbins)
    digangle = np.digitize(np.abs(angle), anglebins)

    for i in np.arange(1, len(speedbins)):
        for j in np.arange(1, len(anglebins)):
            ax = fig.add_subplot(len(speedbins)-1, len(
                anglebins)-1, (i-1) * (len(anglebins)-1) + (j-1) + 1)
            ax.hist(bsp[(digspeed == i) & (digangle == j)].flatten(), range=[0, 6], bins=12)
            if j == 1:
                ax.set_ylabel('TWS:{0:1.0f}-{1:1.0f}'.format(speedbins[i-1], speedbins[i]))
            if i == 1:
                ax.set_title('{0:3.0f}-{1:3.0f} deg'.format(anglebins[j-1], anglebins[j]))


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
    sail = math.smooth_gauss(data['sailing'], 20) > 0.99
    norow = math.smooth_gauss(np.abs(data['rowpermin']), 20) < 0.01
    return sail & norow


def near_const(arr, max_diff=0.01):
    '''mark regions with small gradiant in ``arr``

    This is esssentially ``np.abs(np.diff(arr)) < max_diff`` with one element
    added, so that input and output have the same number of elements.

    Parameters
    ----------
    arr : 1-dim array
    max_diff : np.float
        maximum allowed gradiant between two elements

    '''
    con = abs(np.diff(arr)) < max_diff
    myl = con.tolist()
    myl.append(con[-1])
    return np.array(myl)


def group(angle, wind, bsp, speedbins, anglebins, fct=np.median):
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
    fct : function
        Given all bsp values in one (speedbin,anglebin) select on value to
        be used. Common examples are np.median or np.mean

    Returns
    -------
    polar : ndarray([len(speedbins)+1, len(anglebins)])
        This contains the data array with one speed for each (speedbin, anglebin)
    '''
    if (angle.shape != wind.shape) or (angle.shape != bsp.shape):
        raise ValueError('angle, wind and bsp must have same number of elements')

    digspeed = np.digitize(wind, speedbins)
    digangle = np.digitize(np.abs(angle), anglebins)
    polar = np.zeros([len(speedbins)+1, len(anglebins)])
    for i in np.arange(1, len(speedbins)+1):
        for j in np.arange(1, len(anglebins)):
            polar[i, j] = fct(bsp[(digspeed == i) & (digangle == j)])
    return polar


def plot(ax, polardata, speedbins, anglebins,
         color=['r', 'g', 'b', 'y', 'k', 'c', 'orange'],
         padded=True):
    '''Make a polar plot and label it for data in bins.

    Parameters
    ----------
    ax : matplotlib.axis instance
        axis were the plot should be added. Will usually be a polar axis.
    polardata : ndarray([len(speedbins)+1, len(anglebins)])
        Array with the values to be plotted in individual bins.
    speedbins : ndarray
        bin boundaries for speed binning
    anglebins : ndarray
        bin boundaries for angle binning in deg
        Make sure that 180. is included in last bin and not on the boundary.
    color : array
        matplotlib colors used for plotting the line in the diagram
    padded : bool
        If true, polardata starts with row for data below lowest speed bin
        (as output by np.digitize).
    '''
    start = 1 if padded else 0
    for i in np.arange(1, len(speedbins)):
        plot_half_circle(ax, anglebins[0:-1]+np.diff(anglebins)/2., polardata[i, start:],
                         color=color[i], lw=3,
                         label='{0:3.1f}-{1:3.1f} kn'.format(speedbins[i-1], speedbins[i]))
    temp = ax.legend(loc='upper right')


def setup_plot(fig, axtuple=111, maxr=5., returnall=False):
    '''setup a polar plot (axis,  labels etc.)

    Parameters
    ----------
    fig : matplotlib figure instance
    axtuple : string or number
        defines how the ax containes is placed in ``fig``
    returnall : boolean
        If true, return additional output

    Returns
    -------
    aux_ax1 : matplotlib
        Plot in this auxiliary axis (angle in degrees)
    ax : matplot.axis instance

    '''
    # flip
    matrix = np.identity(3)
    matrix[0, 0] = -1
    # matrix[1,1] = -1
    tr_flip = Affine2D(matrix=matrix)

    # rotate
    tr_rotate = Affine2D().translate(-90, 0)
    # scale degree to radians
    tr_scale = Affine2D().scale(np.pi/180., 1.)
    tr = tr_rotate + tr_flip + tr_scale + PolarAxes.PolarTransform()
    grid_locator1 = MaxNLocator(6)
    grid_helper = floating_axes.GridHelperCurveLinear(
        tr, extremes=(0, 180, 0, maxr), grid_locator1=grid_locator1)

    ax1 = floating_axes.FloatingSubplot(fig, axtuple, grid_helper=grid_helper)
    fig.add_subplot(ax1)

    # adjust axis
    ax1.axis["right"].major_ticklabels.set_axis_direction("left")
    ax1.axis["right"].major_ticklabels.set_visible(True)

    ax1.axis["bottom"].set_visible(False)
    ax1.axis["top"].set_axis_direction("top")

    ax1.grid()

    ax1.axis["left"].label.set_text(r"Geschwindigkeit [kn]")
    ax1.axis["top"].label.set_text(r"Windrichtung")

    aux_ax = ax1.get_aux_axes(tr)
    aux_ax.patch = ax1.patch  # for aux_ax to have a clip path as in ax
    ax1.patch.zorder = 0.9  # but this has a side effect that the patch is
                        # drawn twice, and possibly over some other
                        # artists. So, we decrease the zorder a bit to
                        # prevent this.
    if returnall:
        return aux_ax, ax1, grid_helper
    else:
        return aux_ax, ax1


def plot_half_circle(ax, theta, r, **kwargs):
    '''extends ``theta`` and ``r`` to touch the final bin boundaries, then plots

    Parameters
    ----------
    ax : mpl.Axis instance
    theta : np.ndarray
        angles in degrees
    r : np.ndarray
        radius values for plot
    See ``plt.plot`` for a list of accepted keyword arguments.
    '''
    extended_theta = np.hstack([0, theta, 180.])
    extended_r = np.hstack([r[0], r, r[-1]])
    temp = ax.plot(extended_theta, extended_r, **kwargs)


def my_polar(data, drift=False, rawTWA=False, fct=np.median,
             anglebins=np.arange(0, 181., 15.01),
             speedbins=np.arange(1., 16., 3.)):
    '''Group data into arrays for polar diagrams with default settings

    Parameters
    ----------
    data : NX2 data table
    drift : bool
        If true, return drift angle instead of BSP
    rawTWA : bool
        Usually, the grouping is done by the drift corrected TWA,
        i.e. the direction the ship actually moves in.
        If True, the uncorrected TWA is used.
    fct : function
        see documentation of NX2.polar.group
    '''
    con = near_const(math.smooth_gauss(data['BSP'], 10), max_diff=0.007)
    TWSs = math.smooth_expdec(data['TWS'], 10)
    TWAs = math.smooth_expdec(np.abs(data['TWA']), 10)
    conTWA = near_const(TWAs, max_diff=1.5)
    TWAsdrift = np.abs(TWAs) + np.abs(math.bearingdiff180(data.HDC, data.COG))
    ind = con & conTWA & sail(data)
    if not drift:
        if rawTWA:
            return group(TWAs[ind], TWSs[ind], data['BSP'][ind], speedbins,
                         anglebins, fct=fct)
        else:
            return group(TWAsdrift[ind], TWSs[ind], data['BSP'][ind],
                         speedbins, anglebins, fct=fct)
    else:
        DFT = np.abs(math.bearingdiff180(data['HDC'], data['COG']))
        DFTs = math.smooth_expdec(DFT, 10)
        return group(TWAs[ind], TWSs[ind], DFTs[ind], speedbins,
                     anglebins, fct=fct)

csv_header = '''
# {}
#
# Unit: All speeds are in knots (Nautical mile / hour).
#       All angles are in degrees, 0 deg is into the wind and 180 deg is running downwind.
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

def write_polar_csv(filename, data, speedbins, anglebins, title='Polar diagram', **kwargs):
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
