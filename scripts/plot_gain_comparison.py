import astropy.io.fits as pf
import numpy as np
import h5py
import matplotlib.pyplot as plt


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


    f = h5py.File(initfile, mode='r')
    d = f['000000']['tod'][channel]['gain']
    data = {}
    for i, det in enumerate(dets):
        data[det] = np.array([np.arange(len(d[i, :])), d[i, :]])

    return data


def load_bp_gains(channel, sample, target_file='/mn/stornext/u3/eirikgje/data/cassiopeia/chains_debug/chain_c0001.h5'):
#def load_bp_gains(channel, sample, target_file='/mn/stornext/u3/eirikgje/data/cassiopeia/chains_debug_saved/chain_c0001.h5'):
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

    f = h5py.File(target_file, mode='r')
    data = {}
    for j in range(sample+1):
        for i, det in enumerate(dets):
            if det not in data:
                data[det] = []
            d = f['{:06d}'.format(j)]['tod'][channel]['gain']
            data[det].append(np.array([np.arange(len(d[i, :])), d[i, :]]))

    for det in dets:
        data[det] = np.array(data[det])

    return data


ranges = {
    '24M': [0.0033, 0.0037],
    '24S': [0.0053, 0.0058],
    '25M': [0.0070, 0.0082],
    '25S': [0.0066, 0.0083],
    '26M': [0.0054, 0.0061],
    '26S': [0.0064, 0.0072],
    '27M': [0.072, 0.080],
    '27S': [0.060, 0.067],
    '28M': [0.060, 0.067],
    '28S': [0.049, 0.055],
    '18M': [0.063, 0.071],
    '18S': [0.042, 0.0465],
    '23M': [0.0265, 0.0295],
    '23S': [0.0175, 0.02],
    '19M': [0.0345, 0.0380],
    '19S': [0.0225, 0.0245],
    '22M': [0.0151, 0.0161],
    '22S': [0.0156, 0.0167],
    '20M': [0.0386, 0.04],
    '20S': [0.03225, 0.03425],
    '21M': [0.0225, 0.0245],
    '21S': [0.0232, 0.0248]

}

dets = {
    '030': ['27M', '27S', '28M', '28S'],
    '044': ['24M', '24S', '25M', '25S', '26M', '26S'],
#    '070': ['18M', '18S', '19M', '19S', '20M', '20S', '21M', '21S', '22M', '22S', '23M', '23S']

    '070ds1': ['18M', '18S', '23M', '23S'],
    '070ds2': ['19M', '19S', '22M', '22S'],
    '070ds3': ['20M', '20S', '21M', '21S']
}

sample = 4
for channel in ['030', '044', '070ds1', '070ds2', '070ds3']:
#for channel in ['030', '044', '070']:
    npipe_channel = channel
    if channel in ['030', '044']:
        dpc_channel = channel
        bp_channel = channel
    else:
        dpc_channel = '070'
        bp_channel = '070'
    npipe_data = load_npipe_gains(npipe_channel)
    dpc_data = load_dpc_gains(dpc_channel)
    bp_data = load_bp_gains(bp_channel, sample)
    for det in dets[channel]:
        std = np.std(bp_data[det][:, 1, :], axis=0)
        plt.plot(dpc_data[det][0, :], dpc_data[det][1, :], label='DPC')
        plt.errorbar(bp_data[det][-1, 0, :], bp_data[det][-1, 1, :], yerr=std, label='BP')
        plt.plot(npipe_data[det][0, :], npipe_data[det][1, :], label='NPIPE')
        for pid in [3352, 5030, 5484, 10911, 15957, 16455, 21484, 25654, 27110, 27343, 30387, 32763, 38591, 43929]:
            plt.axvline(x=pid)
        plt.legend()
        plt.ylim(ranges[det][0], ranges[det][1])
        plt.savefig("/mn/stornext/u3/eirikgje/figures/gaincomp_{}.png".format(det))
        plt.clf()

#plt.savefig('gaincomp_{}.png'.format(det))
