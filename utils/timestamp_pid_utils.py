import h5py
import numpy as np

def pid2timestamp(pids, ttype='obt', path='/mn/stornext/u3/eirikgje/data/pid_tables/'):
    """ Convert PID to timestamp.

    Arguments:
        pids - array or scalar, string.
        ttype - type of timestamp. 'mjd', 'obt', 'scet', or 'npipe_obt' (last option is scaling obt by 2**-16)
        path - where the timestamp tables can be found.

    Returns:
        Array of timestamps corresponding to input pids.
    """
    fname = path + 'timestamps_030.hdf5'

    data = h5py.File(fname, 'r')
    pid_data = np.array(data['PID']).astype(str)
    if ttype != 'npipe_obt':
        timestamps = np.array(data[ttype.upper()])
    else:
        timestamps = np.array(data['OBT']) * 2**-16
    return timestamps[np.isin(pid_data, pids)]


def timestamp2pid(timestamps, ttype='obt', path='/mn/stornext/u3/eirikgje/data/pid_tables/'):
    """ Convert timestamp to PID.

    Arguments:
        timestamps - array or scalar, float
        ttype - type of timestamp. 'mjd', 'obt', 'scet', or 'npipe_obt' (last option is obt scaled by 2**-16)
        path - where the timestamp tables can be found.

    Returns:
        Array of pids corresponding to input timestamps. A timestamp belongs to a PID if it is >= the timestamp of that PID, and < the timestamp of the next PID.
    """

    fname = path + 'timestamps_030.hdf5'

    data = h5py.File(fname, 'r')
    pid_data = np.array(data['PID']).astype(str)
    sort_indices = np.argsort(pid_data)
    pid_data = pid_data[sort_indices]
    if ttype != 'npipe_obt':
        timestamp_data = np.array(data[ttype.upper()])
    else:
        timestamp_data = np.array(data['OBT']) * 2**-16
    timestamp_data = timestamp_data[sort_indices]
    return pid_data[np.searchsorted(timestamp_data, timestamps, side='right')-1]
