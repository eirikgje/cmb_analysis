from utils import operations


freq = '030'
detector = 1
pids = np.loadtxt('/home/eirik/temp/pid_ranges_030.dat')
pid_filter = np.where(pids[:, 0] == detector)
pids = pids[pid_filter, 2]
sws = np.loadtxt('/home/eirik/temp/smoothing_windows030.dat')
sw_filter = np.where(sws[:, 0] == detector)
sws = sws[sw_filter, 2]
g_data = np.loadtxt('/home/eirik/temp/gain_030.dat')
gain_filter = np.where(g_data[:, 0] == detector)
gains = g_data[gain_filter, 2]
invsigsquared = g_data[gain_filter, 3]

def pid_range_smoothing(gains, pids, invsigsquared, sw):
    for i in range(len(pids)):
        curr_start = pids[i]
        if i + 1 >= len(pids):
            curr_end = len(gains)
        else:
            curr_end = pids[i + 1]
        if curr_end == 0 curr_end = len(gains)
        curr_gains = gains[curr_start-1:curr_end]


def padded_moving_average_variable_windows(data, weights, windows):
    padded_data = pad_data(data, max(windows))
    padded_weights = pad_data(weights, max(windows))
    for i, window in enumerate(windows):

