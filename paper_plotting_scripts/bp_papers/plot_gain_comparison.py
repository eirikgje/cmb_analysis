import astropy.io.fits as pf
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib import rcParams, rc
from matplotlib.ticker import MaxNLocator, StrMethodFormatter, FixedLocator

params = {'savefig.dpi'        : 300, # save figures to 300 dpi
#          'text.usetex': True,
          'font.family': 'sans-serif',
          'xtick.top'          : False,
          'ytick.right'        : True, #Set to false
          'axes.spines.top'    : True, #Set to false
          'axes.spines.bottom' : True,
          'axes.spines.left'   : True,
          'axes.spines.right'  : True, #Set to false@
          'axes.grid.axis'     : 'y',
          'axes.grid'          : False,
          'ytick.major.size'   : 10,
          'ytick.minor.size'   : 5,
          'xtick.major.size'   : 10,
          'xtick.minor.size'   : 5,
          'ytick.major.width'   : 1.5,
          'ytick.minor.width'   : 1.5,
          'xtick.major.width'   : 1.5,
          'xtick.minor.width'   : 1.5,
          'axes.linewidth'      : 1.5,
          #'ytick.major.size'   : 6,
          #'ytick.minor.size'   : 3,
          #'xtick.major.size'   : 6,
          #'xtick.minor.size'   : 3,
}
rcParams.update(params)

def load_dpc_gains(channel, data_dir='/mn/stornext/u3/eirikgje/data/cassiopeia/dpc_gains/'):
    if channel == '030':
        dets = ['27M', '27S', '28M', '28S']
        fname = 'C030-0000-DX12_OSGN-20160728.fits'
    elif channel == '044':
        dets = ['24M', '24S', '25M', '25S', '26M', '26S']
        fname = 'C044-0000-DX12_OSGN-20160728.fits'
    elif channel == '070':
        dets = ['18M', '18S', '19M', '19S', '20M', '20S', '21M', '21S', '22M', '22S', '23M', '23S']
        fname = 'C070-0000-DX12_OSGN-20160728.fits'

#    fnames = ['LFI_{}_LFI{}_001.fits'.format(channel, det) for det in dets]

    data = {}

    f = pf.open(data_dir + fname)
    for i, det in enumerate(dets):
        d = f[i + 3].data
        d = np.array([np.arange(len(d)), 1/d['LFI{}'.format(det)]])
        data[det] = d

    return data


def load_npipe_gains(channel, initfile='/mn/stornext/u3/eirikgje/data/cassiopeia/commander_data/chain_init_WITHNPIPE.h5'):
    if channel == '030':
        channels = ['030',]
        dets = [['27M', '27S', '28M', '28S']]
    elif channel == '044':
        channels = ['044',]
        dets = [['24M', '24S', '25M', '25S', '26M', '26S']]
#    elif channel == '070ds1':
#        dets = ['18M', '18S', '23M', '23S']
#    elif channel == '070ds2':
#        dets = ['19M', '19S', '22M', '22S']
#    elif channel == '070ds3':
#        dets = ['20M', '20S', '21M', '21S']
    elif channel == '070':
        channels = ['070ds1', '070ds2', '070ds3']
        dets = [['18M', '18S', '23M', '23S'], ['19M', '19S', '22M', '22S'], ['20M', '20S', '21M', '21S']]


    data = {}
    for currchan, currdets in zip(channels, dets):
        f = h5py.File(initfile, mode='r')
        d = f['000000']['tod'][currchan]['gain']
        for i, det in enumerate(currdets):
            data[det] = np.array([np.arange(len(d[i, :])), d[i, :]])

    return data


#def load_bp_gains(channel, sample, target_file='/mn/stornext/u3/eirikgje/data/cassiopeia/chains_debug/chain_c0001.h5'):
#def load_bp_gains(channel, sample, target_file='/mn/stornext/u3/eirikgje/data/cassiopeia/chains_debug_saved/chain_c0001.h5'):
def load_bp_gains(channel, samples, target_files=['/mn/stornext/u3/hke/xsan/commander3/v2/chains_BP7_c10/chain_c0001.h5',
                                                  '/mn/stornext/u3/hke/xsan/commander3/v2/chains_BP7_c11/chain_c0001.h5',
                                                  '/mn/stornext/u3/hke/xsan/commander3/v2/chains_BP7_c12/chain_c0001.h5',
                                                  '/mn/stornext/u3/hke/xsan/commander3/v2/chains_BP7_c13/chain_c0001.h5']):
    if channel == '030':
        dets = ['27M', '27S', '28M', '28S']
    elif channel == '044':
        dets = ['24M', '24S', '25M', '25S', '26M', '26S']
    elif channel == '070ds1':
        dets = ['18M', '18S', '23M', '23S']
    elif channel == '070ds2':
        dets = ['19M', '19S', '22M', '22S']
    elif channel == '070ds3':
        dets = ['20M', '20S', '21M', '21S']
    elif channel == '070':
        dets = ['18M', '18S', '19M', '19S', '20M', '20S', '21M', '21S', '22M', '22S', '23M', '23S']

    data = {}
    for target_file in target_files:
        f = h5py.File(target_file, mode='r')
        for j in range(samples+1):
            for i, det in enumerate(dets):
                if det not in data:
                    data[det] = []
                try:
                    d = f['{:06d}'.format(j)]['tod'][channel]['gain']
                except:
                    continue
                data[det].append(np.array([np.arange(len(d[i, :])), d[i, :]]))
        f.close()

    for det in dets:
        data[det] = np.array(data[det])

    return data


ranges = {
    '24M': [0.0034, 0.00365],
    '24S': [0.00545, 0.0058],
    '25M': [0.0077, 0.0083],
    '25S': [0.0075, 0.0083],
    '26M': [0.0057, 0.00615],
    '26S': [0.0067, 0.0072],
    '27M': [0.0765, 0.080],
    '27S': [0.064, 0.067],
    '28M': [0.0615, 0.0645],
    '28S': [0.0505, 0.0535],
    '18M': [0.065, 0.071],
    '18S': [0.0425, 0.0465],
    '23M': [0.0265, 0.0295],
    '23S': [0.018, 0.02],
    '19M': [0.0345, 0.0380],
    '19S': [0.0235, 0.0245],
    '22M': [0.0151, 0.0162],
    '22S': [0.0156, 0.0168],
    '20M': [0.0386, 0.0401],
    '20S': [0.03225, 0.0343],
    '21M': [0.022, 0.0245],
    '21S': [0.0232, 0.0248]

}

dets = {
    '030': ['27M', '27S', '28M', '28S'],
    '044': ['24M', '24S', '25M', '25S', '26M', '26S'],
    '070': ['18M', '18S', '19M', '19S', '20M', '20S', '21M', '21S', '22M', '22S', '23M', '23S']

#    '070ds1': ['18M', '18S', '23M', '23S'],
#    '070ds2': ['19M', '19S', '22M', '22S'],
#    '070ds3': ['20M', '20S', '21M', '21S']
}

plot_subpanels = {
    '030': (2, 2),
    '044': (3, 2),
    '070': (6, 2)
}

plot_legend_locs = {
    '030': (0.25, 0.53),
    '044': (0.55, 0.40),
    '070': (0.195, 0.67)
}

subplot_xsize = 0.6
subplot_ysize = 0.8
subplot_leftmargin = 0.2
subplot_botmargin = 0.2

samples = 400
curr_channel = None
#for channel in ['030', '044', '070ds1', '070ds2', '070ds3']:
for channel in ['030', '044', '070']:
    npipe_channel = channel
    if channel in ['030', '044']:
        if channel == '030':
            factor = 1e2
            factor_str = r"$10^{-2}$"
        else:
            factor = 1e3
            factor_str = r"$10^{-3}$"
        dpc_channel = channel
        bp_channel = channel
        nbins = 4
        ncol=1
    else:
        dpc_channel = '070'
        bp_channel = '070'
        nbins = 3
        factor = 1e2
        factor_str = r"$10^{-2}$"
        ncol=3
    if curr_channel != bp_channel:
        curr_index = 0
        curr_channel = bp_channel
        currfig, axs = plt.subplots(nrows=plot_subpanels[curr_channel][0], ncols=plot_subpanels[curr_channel][1], sharex=True, gridspec_kw={'wspace':0, 'hspace':0, 'left':subplot_leftmargin, 'right':subplot_leftmargin+subplot_xsize, 'bottom':subplot_botmargin, 'top': subplot_botmargin+subplot_ysize})
        axs = axs.flatten()

    npipe_data = load_npipe_gains(npipe_channel)
    dpc_data = load_dpc_gains(dpc_channel)
    bp_data = load_bp_gains(bp_channel, samples)
    detnums = []
    for det in dets[curr_channel]:
        detnum = det[:2]
        detnums.append(detnum)
        detlet = det[-1]
        if detlet == 'M':
            lcolumn=True
        else:
            lcolumn=False
        if detnum in ('18', '24', '27'):
            top = True
        else:
            top =False

        currax = axs[curr_index]
        if curr_index % 2 != 0:
            currax.yaxis.tick_right()
        std = np.std(bp_data[det][:, 1, :], axis=0)
        print(std)
        dpc_artist, = currax.plot(dpc_data[det][0, :], factor*dpc_data[det][1, :], label='DPC', linewidth=0.2)
#        print(dpc_artist)
        bp_artist = currax.errorbar(bp_data[det][-1, 0, :], factor*bp_data[det][-1, 1, :], yerr=std, label='BP', linewidth=0.2)
#        print(bp_artist)
        npipe_artist, = currax.plot(npipe_data[det][0, :], factor*npipe_data[det][1, :], label='NPIPE', linewidth=0.2)
#        print(npipe_artist)
        for pid in [3352, 5030, 5484, 10911, 15957, 16455, 21484, 25654, 27110, 27343, 30387, 32763, 38591, 43929]:
            currax.axvline(x=pid, color='k', alpha=0.2, linewidth=1)
#        currax.legend((dpc_artist, bp_artist, npipe_artist), ('DPC', 'BP', 'NPIPE'))
        currax.set_ylim(factor*ranges[det][0], factor*ranges[det][1])
        currax.set_xlim(0, 45860)
#        currax.set_xlabel("PID")
#        currax.set_ylabel("Test")
#        if lcolumn:
#            currax.set_ylabel(detnum, rotation='horizontal')

#        if top:
#            currax.setgg
#        plt.savefig("/mn/stornext/u3/eirikgje/figures/gaincomp_{}.png".format(det))
#        plt.clf()
        curr_index += 1
        currax.xaxis.get_major_formatter()._usetex = False
        currax.yaxis.get_major_formatter()._usetex = False
        currax.xaxis.set_major_locator(FixedLocator([15000, 30000, 45000]))
#        currax.xaxis.set_major_locator(MaxNLocator(nbins=nbins, prune='both'))#, min_n_ticks=3)
        currax.yaxis.set_major_locator(MaxNLocator(nbins=nbins, prune='both'))#, min_n_ticks=3)
        currax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))
#        currax.xaxis.set_major_locator(FixedLocator(3))
#        currax.yaxis.set_major_locator(FixedLocator(3))
#        print(currax.get_xticklabels())
#        currax.set()
#        currax.set_xticklabels(currax.get_xticklabels())
#        currax.set_yticklabels(currax.get_yticklabels())
#        for tick in currax.get_xticklabels():
#            tick.set_fontname('monospace')
    detinc = subplot_ysize / len(set(detnums))
    currypos = subplot_botmargin + subplot_ysize - detinc /2 - 0.01
#    for i, detnum in enumerate(set(detnums)):
    already_done = []
    for detnum in detnums:
        if detnum in already_done:
            continue
        already_done.append(detnum)
        currfig.text(subplot_leftmargin/2-0.05, currypos, detnum)
        currypos -= detinc
    currfig.text(0.5, subplot_botmargin/2, 'PID', ha='center')
    currfig.text(subplot_leftmargin + subplot_xsize/4, subplot_botmargin+subplot_ysize + 0.04, 'M')
    currfig.text(subplot_leftmargin + 3*subplot_xsize/4, subplot_botmargin+subplot_ysize + 0.04, 'S')
    currfig.text(subplot_leftmargin-0.02, subplot_botmargin + subplot_ysize+0.01, factor_str)
    currfig.text(subplot_leftmargin+subplot_xsize-0.02, subplot_botmargin + subplot_ysize+0.01, factor_str)
#    currfig.text(0.25, )
    currfig.text(subplot_leftmargin/2-0.01, subplot_botmargin+subplot_ysize/2, 'Gain [V/K]', va='center', rotation='vertical')
#    currfig.text(0.25, )
    handles, labels = axs[0].get_legend_handles_labels()
    n_handles = []
    for handle in handles:
        try:
            n_handles.append(handle.lines[0])
        except:
            n_handles.append(handle)
    leg = currfig.legend(n_handles, labels, loc=plot_legend_locs[channel], fontsize='x-small', ncol=ncol)
    for line in leg.get_lines():
        line.set_linewidth(1.0)
    plt.savefig("gaincomp_{}.pdf".format(curr_channel), bbox_inches='tight')

#plt.savefig('gaincomp_{}.png'.format(det))
