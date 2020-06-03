import h5py
import json

def create_PID_to_OD_mapping(planck_dir, out_dir, frequencies=[30, 44, 70]):
    od_range = [91, 1540]
    horn_map = {30: [27, 28], 44: [24, 25, 26], 70:[18, 19, 20, 21, 22, 23]}

    for freq in frequencies:
        for horn in horn_map[freq]:
            pidmap = {}
            for od in range(od_range[0], od_range[1]):
                fname = planck_dir + '/LFI_{:03d}_{}_L2_002_OD{:04d}.h5'.format(freq, horn, od)
                f = h5py.File(fname)
                for pid in f['AHF_info/PID']:
                    pidmap[int(pid)] = od
            with open(out_dir + '/pid_od_map_{}_{}.json'.format(freq, horn), 'w') as pidmapfile:
                json.dump(pidmap, pidmapfile)


def create_SCET_to_OD_mapping(planck_dir, out_dir, frequencies=[30, 44, 70]):
    od_range = [91, 1605]


#def plot_pid(pid_od_map, planck_dir, freq, horn, pid):
