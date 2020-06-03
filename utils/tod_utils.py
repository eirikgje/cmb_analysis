import h5py
import numpy as np

def extract_tod_from_filelist(filelist, detector, thinning_factor=10):
    files = np.loadtxt(filelist, skiprows=1, dtype=str, usecols=(1,))
    data = {}
    i = 0
    for cfile in set(files):
        i += 1
        if i % 100 == 0:
            print(cfile)
        if i % thinning_factor != 0:
            continue
#        else:
#            continue
        f = h5py.File(cfile[1:-1])
        for pid in list(f):
            if pid == 'common': continue
            data[pid] = np.array(f[pid][detector]['tod'])

    return data

# THis is garbage. No point in concatenating scans after each other
#    totlen = np.sum([len(l) for l in data.values()])
#    pids = np.sort(list(data.keys()))
#    outdata = np.zeros(totlen)
#    currid = 0
#    for pid in pids:
#        currlen = len(data[pid])
#        outdata[currid:currid+currlen] = data[pid]
#        currid += currlen
#    return outdata
