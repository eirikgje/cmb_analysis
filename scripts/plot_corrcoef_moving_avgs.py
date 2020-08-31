import numpy as np
import matplotlib.pyplot as plt
from utils import operations

#detectors = ['{}M'.format(i) for i in range(18, 29)]
#detectors.extend(['{}S'.format(i) for i in range(18, 29)])
detectors = {
    '30': ['27M', '27S', '28M', '28S'],
    '44': ['{}M'.format(i) for i in range(24, 27)],
    '70': ['{}M'.format(i) for i in range(18, 24)]
}
detectors['44'].extend(['{}S'.format(i) for i in range(24, 27)]),
detectors['70'].extend(['{}S'.format(i) for i in range(18, 24)])

data_dir = '/home/eirik/data/cassiopeia/run34/'
output_dir = data_dir + '/figures/'

window_size = 500

for band, detset in detectors.items():
    for detector in detset:
        a = np.loadtxt(data_dir + 'tod_{}_corrcoefs.dat'.format(detector))
        b = operations.moving_average(a[:, 1], window_size)
        plt.plot(b)
        plt.savefig(output_dir + 'movav_corrcoefs_{}.png'.format(detector))
        plt.clf()
    for detector in detset:
        a = np.loadtxt(data_dir + 'tod_{}_corrcoefs.dat'.format(detector))
        b = operations.moving_average(a[:, 1], window_size)
        plt.plot(b, label='{}'.format(detector))
    plt.legend()
    plt.savefig(output_dir + 'movav_corrcoefs_band{}.png'.format(band))
    plt.clf()

#    plt.savefig(output_dir + 'movav_corrcoefs_{}.png'.format(detector))
#    plt.clf()

#    for x in range(0, 45000, 3000):
#        plt.xlim(x, x+3000)
#        plt.savefig(output_dir + 'corrcoefs_{}_{}Kto{}K.png'.format(detector, x, x+3000))
#    plt.clf()
