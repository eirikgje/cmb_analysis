import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, rc

params = {'savefig.dpi'        : 300, # save figures to 300 dpi
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

#datadir = '/mn/stornext/d16/cmbco/eirikgje/data/bp_paper_plot_data/'
datadir = '/home/eirik/data/bp_paper_plot_data/'

data = np.loadtxt(datadir + 'tod_24S_pid009495.dat')

plt.plot(data[:, 9])
plt.plot(data[:, 8])
plt.xlim(0, 10000)

plt.xlabel('Sample number')
plt.ylabel('Temperature (K)')

plt.savefig('dipole_comparison.png', bbox_inches='tight')
