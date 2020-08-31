import matplotlib.pyplot as plt
import numpy as np

detectors = ['{}M'.format(i) for i in range(18, 29)]
detectors.extend(['{}S'.format(i) for i in range(18, 29)])

data_dir = '/home/eirik/data/cassiopeia/run34/'
output_dir = data_dir

for detector in detectors:
    a = np.loadtxt(data_dir + 'tod_{}_corrcoefs.dat'.format(detector))
    plt.plot(a[:, 0], a[:, 1])
    plt.savefig(output_dir + 'corrcoefs_{}.png'.format(detector))
    for x in range(0, 45000, 3000):
        plt.xlim(x, x+3000)
        plt.savefig(output_dir + 'corrcoefs_{}_{}Kto{}K.png'.format(detector, x, x+3000))
    plt.clf()
