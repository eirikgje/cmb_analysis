import numpy as np
import matplotlib.pyplot as plt

pidlist = [15000, 10000, 1000, 24000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]
#pidlist = [4000, 7000]

sampnum = 2

fig, ax = plt.subplots()
data_dir = "/home/eirik/data/cassiopeia/"
#data_dir = "/home/eirik/data/cassiopeia/run44/"
#data_dir = "/home/eirik/data/cassiopeia/run46/"
#data_dir = "/home/eirik/data/cassiopeia/run45/"
#data_dir = "/home/eirik/data/cassiopeia/run43/"
#data_dir = "/home/eirik/data/cassiopeia/run47/"
#data_dir = "/home/eirik/data/cassiopeia/"
info = {'CMB (Scan opposite to dipole axis)': [4000, 'run43'],
        'CMB (Scan along dipole axis)': [7000, 'run43'],
#        'Synchrotron': [15000, 'run44'],
        'Free-free': [15000, 'run46'],
        'AME': [15000, 'run47'],
        'Thermal dust': [15000, 'run49']}
detector = '27M'

for label, info_item in info.items():
    pid = info_item[0]
    currdata = np.loadtxt(data_dir + info_item[1] + "/tod_{}_pid{:06d}_k{:06d}.dat".format(detector, pid, sampnum))
    s_sky = currdata[:, -2]
    s_orb = currdata[:, -1]
    s_tot = currdata[:, -3]
    mask = currdata[:, 2]
    tod = currdata[:, 3]
    ax.plot(s_sky, label=label)

#ax.plot(mask*max(s_sky), label='mask')

ax.set_xlim(0, 3000)
ax.set_xlabel("PID")
ax.set_ylabel("Signal [K]")
#ax.set_ylim(-0.004, 0.004)
ax.legend()
plt.savefig('signal_comparison.png', bbox_inches='tight')
plt.savefig('signal_comparison.pdf', bbox_inches='tight')
