import datetime

import matplotlib.pyplot as plt
import matplotlib


def plot_speeds(self, t1=(0, 0, 0), t2=(23, 59, 59), second=['HDC']):
        '''Return a figure that shows BSP, SOG and rowing (if posible)
        '''
        fig = plt.figure()
        fig.canvas.set_window_title('Bootsgeschwindigkeit')
        axang = fig.add_axes([0.1, 0.1, 0.8, 0.4])  # left, bottom, width, height
        ax = fig.add_axes([0.1, 0.5, 0.8, 0.4], sharex=axang)
        ax2 = ax.twinx()

        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S', tz=None))
        # plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

        ind = (self.time() >= datetime.time(*t1)) & (self.time() <= datetime.time(*t2))

        sog = ax.plot(self.datetime()[ind], self.SOG[ind], label='SOG')
        bsp = ax.plot(self.datetime()[ind], self.BSP[ind], label='BSP')
        lab = plt.ylabel('Geschwindigkeit in Knoten')
        lab = plt.xlabel('Uhrzeit')

        if 'sailing' in self.keys():
            # sailind = (ind & (self.sailing == 1))
            ax.plot(self.datetime()[ind], self.sailing[ind], 'bs', label='Sailing')
        # plt.xticks(rotation=45)
        if 'rowpermin' in self.keys():
            index = self.minutes_index() & ind
            minutes = np.array(map(lambda x: x.replace(
                second=0, microsecond=0), self.datetime()[index]))
            row = ax2.bar(minutes, self.rowpermin[
                          index], label=u'Ruderschläge', width=1./24./60., linewidth=0., alpha=0.4, color='r')
            ax2.set_ylabel(u'Ruderschläge', color='r')
            ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:S', tz=None))
            for tl in ax2.get_yticklabels():
                tl.set_color('r')

        for value in second:
            axang.plot(self.datetime()[ind], self[value][ind], label=value)
            if value in ['HDC']:
                axang.set_ylim([0, 360])
        axang.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S', tz=None))
        for a in [ax, axang]:
            xlab = a.get_xticklabels()
            for label in xlab:
                label.set_rotation(30)
        return fig


def plotall(data, day, t1=(0,0,0), t2=(23,59,59), scale=50, n=300, secondplot=['HDC']):
    d = data.where(data.day == day)
    d = d.when(t1, t2)
    plot_speeds(d, second=secondplot)
    d.plot_course(scale=scale, n=n)

def turn_speed(data, day, t1=(0,0,0), t2=(23,59,59)):
    d = data.where(data.day == day)
    d = d.when(t1, t2)
    t  = d.datetime()
    dt = t[-1] - t[0]
    print (d.HDC[-1] - d.HDC[0]) / dt.total_seconds()
