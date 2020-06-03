from scipy.io import FortranFile
import numpy as np

def read_covmat(fname):
    with FortranFile(fname) as f:
        n = f.read_ints(dtype=np.int32)
        ordering = f.read_ints(dtype=np.int32)
        polarization = f.read_ints(dtype=np.int32)
        mat = []
        for i in range(n[0]):
            mat.append(f.read_reals(dtype=np.float))
        if ordering[0] == 2:
            ordering = 'nest'
        else:
            ordering = 'ring'
    mat = np.array(mat)
    diag = []
    for i in range(n[0]):
        diag.append(mat[i, i])
    covmat = {'data': mat,
              'ordering': ordering,
              'polarization': polarization[0],
              'n': n[0],
              'diag': np.array(diag)}
    return covmat


def extract_fname(full_fname):
    """ Given a full file path, extracts the file name part of the string. 

    Arguments:
        full_fname (string): The full path to the file.

    Returns:
        The filename part of the string.
    """
    return full_fname.split('/')[-1]
