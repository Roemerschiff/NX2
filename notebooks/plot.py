import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def course(df, scale=5, n=300, keyscale=1, **kwargs):
    ax = df.plot('x', 'y', legend=False, color='#55AAFF', label='kein Segel',
                 **kwargs)
    df.plot('x_Segel_masked', 'y', color='b', lw=3, ax=ax, label='Segel')
    ax.legend(loc='lower left')

    # vectors
    dn = df.loc[::n]

    quiver_wind = ax.quiver(dn['x'], dn['y'],
                            dn['TWS'] * np.sin(np.deg2rad(dn['windang'])),
                            dn['TWS'] * np.cos(np.deg2rad(dn['windang'])),
                            scale=scale, scale_units='inches')
    quiver_bsp = ax.quiver(dn['x'], dn['y'],
                           dn['BSP'] * np.sin(np.deg2rad(dn['HDC'])),
                           dn['BSP'] * np.cos(np.deg2rad(dn['HDC'])),
                           scale=scale, scale_units='inches',
                           color='g')
    quiver_sog = ax.quiver(dn['x'], dn['y'],
                           dn['SOG'] * np.sin(np.deg2rad(dn['COG'])),
                           dn['SOG'] * np.cos(np.deg2rad(dn['COG'])),
                           scale=scale, scale_units='inches',
                           color='salmon')

    qk_wind = ax.quiverkey(quiver_wind, .1, 0.95, keyscale,
                           'Wind', labelpos='E')
    qk_bsp = ax.quiverkey(quiver_bsp, .1, 0.9, keyscale,
                          'Fahrt durchs Wasser (ohne Drift)', labelpos='E')
    qk_sog = ax.quiverkey(quiver_sog, .1, 0.85, keyscale,
                          'Fahrt über Grund', labelpos='E')
    ax.set_xlabel('West - Ost [Meter]')
    ax.set_ylabel('Süd - Nord [Meter]')
    ax.set_aspect('equal')
    return ax


def speeds(df, **kwargs):
    ax = df.plot(y=['SOG', 'BSP'], **kwargs)
    pd.plotting.register_matplotlib_converters()
    if ('Segel' in df.columns) or ('Ruderschlaege/Minute' in df.columns):
        axt = plt.twinx(ax)
        axt.set_ylabel('Ruderschläge', color='g')
        for tl in axt.get_yticklabels():
                tl.set_color('g')
    if 'Segel' in df.columns:
        axt.fill_between(df['time'], -50, 50, where=df['Segel'] == 1,
                         color='0.5', alpha='.4', zorder=0, label='Segel')
    if 'Ruderschlaege/Minute' in df.columns:
        axt.fill_between(df['time'], df['Ruderschlaege/Minute'],
                         alpha=0.4, color='g',
                         step='pre', label='Ruderschlaege / min')
    ax.set_ylabel('Geschwindigkeit in Knoten')
    ax.set_xlabel('Uhrzeit')
    return ax


def fit_BSP(df, plot=True, **kwargs):
    con1 = df['BSP'] > 0  # moving
    con2 = np.abs(df['COG'] - df['HDC']) < 15.
    con3 = np.abs(df['BSP_s'].diff()) < 0.01
    ind = con1 & con2 & con3

    x = df.loc[ind]['SOG']
    y = df.loc[ind]['BSP']
    # Linear regression through origin
    a = np.dot(x, y) / np.dot(x, x)

    if plot:
        ax = df.plot('SOG', 'BSP', kind='scatter', alpha=.2, s=5,
                     label='Datenpunkte (verworfen)', **kwargs)
        df.loc[ind].plot('SOG', 'BSP', kind='scatter', s=5, ax=ax,
                         label='Datenpunkte (genutzt)', color='k')
        xlim = np.array(ax.get_xlim())
        ax.plot(xlim, a * xlim, 'r', label='fit')
        ax.set_xlim(0, None)
        ax.set_ylim(0, None)
        ax.legend()
        ax.set_xlabel('Fahrt über Grund [Knoten]')
        ax.set_ylabel('Fahrt im Wasser [Knoten]')
        return a, ind, ax
    else:
        return a, ind


def make_polar(df, anglebins=np.arange(0, 181., 15.01),
               speedbins=np.arange(1., 16., 3.),
               anglecol='absTWA_drift_s', speedcol='TWS_s'):
    df['ang_bin'] = pd.cut(df[anglecol], anglebins)
    df['v_bin'] = pd.cut(df[speedcol], speedbins)
    dp = df.loc[(df['Segel'] == 1) &
                (df['row_s'] < 0.1) &
                (np.abs(df['BSP_s'].diff()) < 0.007) &
                (np.abs(df['absTWA_s'].diff()) < 1.)]
    polar = dp.groupby(['ang_bin', 'v_bin'])
    return polar, dp


def polar(polard, ax=None, labeltext='{:2.0f}-{:2.0f} kn', look='smooth',
          **kwargs):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
    for label, col in polard.iteritems():
        if look == 'bins':
            ang = np.stack([col.index.categories.left,
                            col.index.categories.right]).T.flatten()
            r = np.repeat(col, 2)
        else:
            # Add one point at 180 deg at the end to close contour to axis
            ang = np.append(col.index.categories.mid, 180.)
            r = np.append(col, col[-1])
        ax.plot(np.deg2rad(ang), r, label=labeltext.format(label.left,
                                                           label.right),
                **kwargs)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_theta_zero_location('N')
    ax.set_xticks(np.deg2rad(range(0, 181, 45)))
    return ax
