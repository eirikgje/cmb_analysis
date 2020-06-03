import numpy as np
import healpy

def radii2mask(nside, centers, radii, inclusive=True, fact=4, 
               ordering='ring'):
    """ Gives an array of pixels included in a list of centers and a radius.
    
    Arguments:
        nside (int): Nside of the map.
        centers (tuple of two np.arrays): The theta, phi coordinates of the
            centers.
        radii (np.array of same size as the arrays in centers): The radii, in
            radians, of the circles around the centers that we want to mask.
        inclusive (bool): If False, mask the exact set of pixels whose pixel
            centers lie within the disk; if True, mask all pixels that overlap
            with the disk, perhaps a few more.
        fact (integer): Only used when inclusive=True. The overlapping test
            will be done at the resolution fact*nside.
        ordering (string): 'ring' or 'nested'.

    Returns:
        Array of booleans where the specified circles are masked out.
    """

    centers_vecs = healpy.dir2vec(centers, lonlat=True)

    mask = np.ones(12 * nside ** 2, dtype=np.bool)

    num = 0
    if ordering == 'ring':
        nest = False
    elif ordering == 'nested':
        nest = True
    for center, radius in zip(centers_vecs.transpose(), radii):
        if radius == 0:
            continue
        mask[healpy.query_disc(nside, center, radius, inclusive=inclusive,
                               fact=fact, nest=nest)] = 0
    return mask


def calc_snr_dep_radii(amplitude, noise, fwhm):
    """ Calculate SNR-dependent radii around sources.

    This uses the algorithm provided by Marcos Caniego-Lopez.

    Arguments:
        amplitude (np.array): The amplitudes (signals) of each source.
        noise (np.array): The noise of each source.
        fwhm (float):  The FWHM in arcmin.

    Returns:
        list of floats containing the radius around each source.
    """
    # Hardcoded to be the value used in Planck
    m = 0.1
    radii = np.zeros(len(amplitude))
    pos_filter = amplitude > 0
    beam_frac = np.sqrt(2 * np.log(np.array(amplitude[pos_filter]) /
                                   np.array(noise[pos_filter]) / m))
    radii[pos_filter] = (fwhm / 60.0 / 180.0 * np.pi / 
                         (2 * np.sqrt(2 * np.log(2))) * beam_frac)
    return list(radii)
