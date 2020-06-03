import healpy
import numpy as np
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

my_cmap = ListedColormap(np.loadtxt('/home/eirik/data/Planck_Parchment_RGB.txt')/255.)
directory = '/home/eirik/data/cassiopeia/run12/'

mapfile = directory + 'tod_044_ncorr_c0001_k000015.fits' 
descriptive_text = 'full'
#descriptive_text = 'survey8'
#descriptive_text = 'full'
limits = 5

a = healpy.read_map(mapfile, field=None)
a_smoothed = healpy.smoothing(a, fwhm=3 * np.pi/180)
a_filtered = a_smoothed.copy()
a_filtered[np.abs(a_filtered) > 15] = 0

for i, text in enumerate(['T', 'Q', 'U']):
    healpy.mollview(a_smoothed[i], cmap=my_cmap, min=-limits, max=limits)
    plt.savefig(directory + 'ncorr_{}_{}_44GHz_smoothed_3deg_imposedlimits.png'.format(text, descriptive_text))
    healpy.mollview(a_smoothed[i], cmap=my_cmap)
    plt.savefig(directory + 'ncorr_{}_{}_44GHz_smoothed_3deg.png'.format(text, descriptive_text))
    healpy.mollview(a_filtered[i], cmap=my_cmap)
    plt.savefig(directory + 'ncorr_{}_{}_44GHz_smoothed_3deg_filtered.png'.format(text, descriptive_text))
    healpy.mollview(a[i], cmap=my_cmap, min=-limits, max=limits)
    plt.savefig(directory + 'ncorr_{}_{}_44GHz_imposedlimits.png'.format(text, descriptive_text))
