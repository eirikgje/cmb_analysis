import h5py
import numpy as np

filelists = {
    '30': '/mn/stornext/d16/cmbco/eirikgje/data/cassiopeia/commander_data/filelist_30_v14.txt',
    '44': '/mn/stornext/d16/cmbco/eirikgje/data/cassiopeia/commander_data/filelist_44_v14.txt',
    '70': '/mn/stornext/d16/cmbco/eirikgje/data/cassiopeia/commander_data/filelist_70_v14.txt',
}

pidarr = {}

for det, fname in filelists.items():
    currfiles = np.loadtxt(fname, skiprows=1, dtype=str, usecols=(1,))
    pidarr[det] = []
    i = 0
    for cfile in set(currfiles):
        i += 1
        if i % 100 == 0:
            print(cfile)
        f = h5py.File(cfile[1:-1])
        for pid in list(f):
            if pid == 'common': continue
            pidarr[det].append([pid] + list(f[pid]['common']['time']))

    hf = h5py.File('timestamps_{}.hdf5'.format(det))
    hf.create_dataset('/PID', data=np.array([el[0] for el in pidarr[det]], dtype=np.string_))
    hf.create_dataset('/MJD', data=np.array([el[1] for el in pidarr[det]]))
    hf.create_dataset('/OBT', data=np.array([el[2] for el in pidarr[det]]))
    hf.create_dataset('/SCET', data=np.array([el[3] for el in pidarr[det]]))
    hf.close()
