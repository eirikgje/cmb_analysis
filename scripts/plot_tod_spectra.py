import numpy as np
import matplotlib.pyplot as plt

#data_dir = '/home/eirik/data/cassiopeia/run39/'
#output_dir = '/home/eirik/data/cassiopeia/run39/figures/'

data_dir = '/home/eirik/data/cassiopeia/debug_run39/'
output_dir = '/home/eirik/data/cassiopeia/debug_run39/figures/'

for i in range(100, 5100, 100):
    for t in ['abs', 'rel']:
        dfile = data_dir + 'gainfit_{}_{:05d}.dat'.format(t, i)
        data = np.loadtxt(dfile)
        start_inds = np.where(data[:, 0] == 1)[0]
        print(start_inds)
        print(len(data))
        print(i)
        residual, s_ref, s_invN, s_sub, tod, downsampled_tod, filled_tod, mask = data[:start_inds[1], :], data[start_inds[1]:start_inds[2], :], data[start_inds[2]:start_inds[3], :], data[start_inds[3]:start_inds[4], :], data[start_inds[4]:start_inds[5], :], data[start_inds[5]:start_inds[6], :], data[start_inds[6]:start_inds[7], :], data[start_inds[7]:, :]
        n_tod = len(tod)
        n_downsampled = len(downsampled_tod)

        x_downsampled = np.fft.rfftfreq(n_downsampled, 1.0)
        x_tod = np.fft.rfftfreq(n_tod, n_downsampled/n_tod)

        f_tod = np.fft.rfft(tod[:, 1])
        f_downsampled = np.fft.rfft(downsampled_tod[:, 1])
        f_filled = np.fft.rfft(filled_tod[:, 1])

        plt.loglog(x_tod, np.abs(f_tod)**2 / n_tod **2)
        plt.loglog(x_tod, np.abs(f_filled) **2 / n_tod **2)
        plt.loglog(x_downsampled, np.abs(f_downsampled)**2 / n_downsampled**2)
        plt.savefig(output_dir + 'tod_spectra_{}_{:05d}.png'.format(t, i))
        plt.clf()
