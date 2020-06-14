# -*- coding: utf-8 -*-

from glob import glob
import os
import re
import warnings

import numpy as np

import NX2


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
    return day, month, year


def NX2_for_year(filelist, rowfile, corr_bsp=1.):
    dat = []
    with warnings.catch_warnings():
        for f in filelist:
            data = NX2.NX2Table(f, date_from_filename(f),
                                corr_bsp=corr_bsp, verbose=False)
            data.add_rowing_old_format(rowfile, verbose=False)
            dat.append(data)
    return dat


def merge_NX2list(NX2list):
    merged = NX2list[0]
    for i in np.arange(1, len(NX2list)):
        merged.append(NX2list[i])
    return merged


def read_06(datapath):
    with warnings.catch_warnings():
        dat0651 = NX2.NX2Table(os.path.join(datapath, '2006/fifth-day-no-sail23-06-2006.00.csv'), (23,06,2006), origin = (49.0164, 12.0285), corr_bsp = 1./0.9, verbose = False)
        dat0651.add_rowing_old_format(os.path.join(datapath, '2006/Ruderschlaege.csv'), verbose = False)
        NX2.NX2.remove_Danube_current(dat0651)
        dat0661 = NX2.NX2Table(os.path.join(datapath, '2006/sixth-day-with-sail24-06-2006.00.csv'), (24,06,2006), origin = (49.0164, 12.0285), corr_bsp = 1./0.9, verbose = False)
        dat0661.add_rowing_old_format(os.path.join(datapath, '2006/Ruderschlaege.csv'), verbose = False)
        NX2.NX2.remove_Danube_current(dat0661)
        dat0651.append(dat0661)
    return dat0651


def read_08(datapath):
    filelist = glob(os.path.join(datapath, '2008', '*csv'))
    rowfile08 = glob(os.path.join(datapath, '2008', 'Ruderschlaege*.csv'))[0]
    filelist.sort()
    filelist.remove(rowfile08)
    # file almost empty, BSP missing, a few min only
    filelist.remove(os.path.join(datapath, '2008','080504sixteenthday_sail.00.csv'))
    dat08 = NX2_for_year(filelist, rowfile08, corr_bsp=1. / 1.18)
    d08 = merge_NX2list(dat08)
    return d08


def read_11(datapath):
    filelist = glob(os.path.join(datapath, '2011', '*csv'))
    rowfile11 = glob(os.path.join(datapath, '2011', 'Ruderschlaege*.csv'))[0]
    filelist.sort()
    filelist.remove(rowfile11)
    filelist.remove(os.path.join(datapath, '2011', 'Test_Hamburg_110415.00.csv'))
    dat11 = NX2_for_year(filelist, rowfile11, corr_bsp=1. / 0.87)
    d11 = merge_NX2list(dat11)
    return d11


def read_12(datapath):
    filelist = glob(os.path.join(datapath, '2012', '*csv'))
    filelist.sort()
    rowfile12 = glob(os.path.join(datapath, '2012', 'Ruderschlaege*.csv'))[0]
    filelist.remove(rowfile12)
    filelist.remove(os.path.join(datapath, '2012', '20120514_TestSystem.00.csv'))
    dat12 = NX2_for_year(filelist, rowfile12, corr_bsp=1. / 0.87)
    d12 = merge_NX2list(dat12)
    return d12
