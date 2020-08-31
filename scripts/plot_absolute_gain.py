import numpy as np
import matplotlib.pyplot as plt

data_dir = '/home/eirik/data/cassiopeia/debug_run40/'
output_dir = data_dir + '/figures/'

detectors = {
    '030': ['27M', '27S', '28M', '28S'],
    '044': [detector for i in range(24, 27) for detector in ['{}S'.format(i), '{}M'.format(i)]],
    '070': [detector for i in range(18, 24) for detector in ['{}S'.format(i), '{}M'.format(i)]]
}

for band, detset in detectors.items():
    band_data = np.loadtxt(data_dir + 'gain0_{}.dat'.format(band))
    currind = 0
    for det in detset:
        gain = band_data[currind:currind+45860, 2]
        unc = band_data[currind:currind+45860, 3]
        plt.plot(gain)
        print('Plotting gain')
        plt.savefig(output_dir + 'gain_{}.png'.format(det))
        print('Saving')
        plt.clf()
        print('CLEARING')
        plt.plot(unc)
        print('Plotting uncertainty')
        plt.savefig(output_dir + 'unc_{}.png'.format(det))
        plt.clf()
        print("CLF")
        plt.plot(gain)
        plt.plot(unc)
        plt.savefig(output_dir + 'both_{}.png'.format(det))
        currind += 45860
