from calculation import tod_calcs as tc
import matplotlib.pyplot as plt
import numpy as np
import os.path

sampling_frequencies = {'44': 46.545454545454}
pids = np.arange(40569, 41232)
tod_dir = '/home/eirik/data/cassiopeia/run33/tods/'
output_dir = '/home/eirik/temp/phase_plots/'
band = '44'
detectors = ['24S', '24M', '25S', '25M', '26S', '26M']
bin_width = 1 # seconds
target_period = 60 # seconds

for detector in detectors:
    for pid in pids:
        pid_string = '{:06d}'.format(pid)

        datafile = tod_dir + 'tod_{}_pid{}.dat'.format(detector, pid_string)
        if not os.path.exists(datafile): continue

        data = np.loadtxt(datafile)
        tod = data[:, 1]
        ncorr = data[:, 5]
        stot = data[:, 7]

        binned_data = tc.bin_phases(tod, sampling_frequencies[band], bin_width, target_period)
        plt.plot(binned_data)
        plt.savefig(output_dir + 'tod_phased_{}_pid_{}.png'.format(detector, pid_string))
        plt.clf()

        binned_data = tc.bin_phases(ncorr, sampling_frequencies[band], bin_width, target_period)
        plt.plot(binned_data)
        plt.savefig(output_dir + 'ncorr_phased_{}_pid_{}.png'.format(detector, pid_string))
        plt.clf()

        binned_data = tc.bin_phases(stot, sampling_frequencies[band], bin_width, target_period)
        plt.plot(binned_data)
        plt.savefig(output_dir + 'stot_phased_{}_pid_{}.png'.format(detector, pid_string))
        plt.clf()
