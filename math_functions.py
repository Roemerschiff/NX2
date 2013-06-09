import numpy as np
import scipy.stats
from scipy.signal import convolve

def smooth_expdec(data, t_e):
    '''smooth an array with an exponential decay

    :param data: input array to be smoothed
    :param t_e: decay timescale of expoential in number of bins
        (for NX2 data, i.e. seconds)'''
    kernel = np.zeros(2*3*t_e+1)
    kernel[3*t_e:-1] = np.exp(-np.arange(3*t_e, dtype = np.float)/t_e)
    kernel = kernel / kernel.sum()
    return np.convolve(data,kernel,'same')

def smooth_gauss(data, width):
    '''smooth an array with a gauss

    :param data: input array to be smoothed
    :param width: width of gauss distribution in number of bins
        (for NX2 data, i.e. seconds)'''
    norm = scipy.stats.norm(0.,width)
    kernel = norm.pdf(np.arange(-3.*width,3.001*width))
    kernel = kernel / kernel.sum()
    return np.convolve(data,kernel,'same')

