from calculation import tod_calcs as tc
import matplotlib.pyplot as plt
import numpy as np
import os.path

sampling_frequencies = {'44': 46.5454545454545,
                        '70': 78.7692307692308,
                        '30': 32.5079365079365}
pids = np.arange(40569, 41232)
tod_dir = '/home/eirik/data/cassiopeia/run33/tods/'
output_dir = '/home/eirik/temp/phase_plots/'
band = '44'
detectors = ['24S', '24M', '25S', '25M', '26S', '26M']
bin_width = 1 # seconds
target_period = 60 # seconds

for detector in detectors:
    corrcoefs = []
    random_corrcoefs = []
    for pid in pids:
        pid_string = '{:06d}'.format(pid)

        datafile = tod_dir + 'tod_{}_pid{}.dat'.format(detector, pid_string)
        if not os.path.exists(datafile): 
            corrcoefs.append(0)
            random_corrcoefs.append(0)
            continue

        data = np.loadtxt(datafile)
#    tod = data[:, 1]
        ncorr = data[:, 5]
        s_tot = data[:, 7]

        binned_ncorr = tc.bin_phases(ncorr, sampling_frequencies[band], bin_width, target_period)
        binned_s_tot = tc.bin_phases(s_tot, sampling_frequencies[band], bin_width, target_period)
        random = np.random.rand(len(binned_ncorr))
        corrcoefs.append(np.corrcoef(binned_ncorr, binned_s_tot)[0, 1])
        random_corrcoefs.append(np.corrcoef(binned_ncorr, random)[0, 1])

    corrcoefs = np.array(corrcoefs)
    random_corrcoefs = np.array(random_corrcoefs)
    zeromask = corrcoefs != 0
    print("Detector: {}".format(detector))
    print("Std")
    print(np.std(corrcoefs[zeromask]))
    print("Random std")
    print(np.std(random_corrcoefs[zeromask]))

    plt.plot(pids, corrcoefs)
    plt.plot(pids, random_corrcoefs)
    plt.savefig(output_dir + 'corrcoefs_{}.png'.format(detector))
    plt.clf()
