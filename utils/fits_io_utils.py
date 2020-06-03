import astropy.io.fits as pf
import numpy as np
import healpy
from utils import map_utils, fits_utils


def read_planck_fullmap(fname, unit_map, field=0, nest=False,
                        dtype=np.float64, verbose=True, extension=1,
                        extract_comments=False):
    """ Reads a FITS file containing one or more HEALPix maps from PLA.

    This routine is mostly copied from healpy.read_map with some minor changes
        to accommodate our needs.

    Arguments:
        fname (string): The filename of the map.
        field (integer, iterable): Which field(s) to load.
        dtype (numpy dtype): To which data type the data should be cast. None
            means that the data type will be inferred from the FITS header.
        verbose(bool): If True, print a number of diagnostic messages.
        extension (integer): If the file contains several extensions containing
            data, specifies which we should read from.
        extract_comments (bool): Whether to propagate the comments in the FITS
            header to the output map object.

    Returns:
        Map object containing the specified data.
    """

    hdulist = pf.open(fname)
    fits_hdu = hdulist[extension]

    nside = fits_hdu.header['NSIDE']
    nside = int(nside)

    if not healpy.pixelfunc.isnsideok(nside):
        raise ValueError('Wrong nside parameter.')

    ordering = fits_hdu.header['ORDERING']

    sz = healpy.pixelfunc.nside2npix(nside)
    ret = []

    if field is None:
        field = range(len(fits_hdu.data.columns))
    elif not (hasattr(field, '__len__') or isinstance(field, basestring)):
        field = (field,)

    if dtype is None:
        dtype = []
        for i in field:
            dtype.append(fits_utils.fits2numpyformat(
                fits_hdu.header['TFORM%d' % (i+1)]))
    else:
        try:
            assert len(dtype) == len(field), """The number of dtypes are not
                equal to the number of fields"""
        except TypeError:
            dtype = [dtype] * len(field)

    for ff, curr_dtype in zip(field, dtype):
        try:
            m = fits_hdu.data.field(ff).astype(curr_dtype).ravel()
        except pf.VerifyError as e:
            print(e)
            print("Trying to fix a badly formatted header")
            m = fits_hdu.verify("fix")
            m = fits_hdu.data.field(ff).astype(curr_dtype).ravel()

        if (not healpy.pixelfunc.isnpixok(m.size) or
                (sz > 0 and sz != m.size)):
            raise ValueError('Wrong nside parameter.')
        if nest is not None:  # no conversion with None
            if nest and ordering == 'RING':
                idx = healpy.pixelfunc.nest2ring(
                    nside,
                    np.arange(m.size, dtype=np.int32))
                m = m[idx]
                if verbose:
                    print('Ordering converted to NEST')
            elif (not nest) and ordering == 'NESTED':
                idx = healpy.pixelfunc.ring2nest(nside,
                                                 np.arange(m.size,
                                                           dtype=np.int32))
                m = m[idx]
                if verbose:
                    print('Ordering converted to RING')
        try:
            m[healpy.pixelfunc.mask_bad(m)] = healpy.UNSEEN
        except OverflowError:
            pass
        ret.append(m)
    if nest is not None:
        ordering = ('nested' if nest else 'ring')
    else:
        ordering = ordering.lower()

    comments = []
    if extract_comments:
        comments = fits_utils.extract_header_comments(fits_hdu.header.cards)

    return map_utils.bundle_fullmap(ret, header=list(fits_hdu.header.cards),
                                    ordering=ordering,
                                    header_filter=list(field),
                                    unit_map=unit_map,
                                    comments=comments)


def write_planck_fullmap(fname, fmap):
    """ Writes a map to a FITS file.

    This routine is mostly copied from healpy.write_map with some minor changes
        to accommodate our needs.

    Arguments:
        fname (string): The filename (including path) of the output file.
        fmap (map object): The map object to save.

    Returns:
        None
    """

    m = fmap['data']
    header = fits_utils.prepare_header(fmap)

    if not hasattr(m, '__len__'):
        raise TypeError('The map must be a sequence')

    m = healpy.pixelfunc.ma_to_array(m)
    if healpy.pixelfunc.maptype(m) == 0:  # a single map is converted to a list
        m = [m]

    # We collect column units, names, and formats from the input header
    column_names = []
    column_units = []
    fitsformat = []

    for args in header:
        if args[0].startswith('TTYPE'):
            column_names.append(args[1])
        elif args[0].startswith('TFORM'):
            fitsformat.append(args[1])
        elif args[0].startswith('TUNIT'):
            column_units.append(args[1])

    # maps must have same length
    assert len(set(map(len, m))) == 1, "Maps must have same length"
    nside = healpy.pixelfunc.npix2nside(len(m[0]))

    if nside < 0:
        raise ValueError('Invalid healpix map : wrong number of pixel')

    cols = []

    for cn, cu, mm, curr_fitsformat in zip(column_names, column_units, m,
                                           fitsformat):
        cols.append(pf.Column(name=cn,
                              format='%s' % curr_fitsformat,
                              array=mm,
                              unit=cu))
    tbhdu = pf.BinTableHDU.from_columns(cols)

    currpos = len(tbhdu.header)
    for args in header:
        if (args[0].startswith('TTYPE') or args[0].startswith('TFORM') or
                args[0].startswith('TUNIT')):
            tbhdu.header.set(args[0], value=args[1], comment=args[2],
                             after=currpos)
            currpos += 1
            continue
        elif (args[0] != 'COMMENT' and args[0] in tbhdu.header):
            continue
        tbhdu.header.insert(currpos, args, after=True)
        currpos += 1

    tbhdu.writeto(fname, clobber=True)


def read_planck_cutout(fname, unit_map, extract_comments=False):
    """ Reads a FITS file containing one or more cutout maps from PLA.

    Arguments:
        fname (string): The file name (including path) of the cutout.
        extract_comments (bool): Whether to propagate the comments in the FITS
            header to the output map object.

    Returns:
        Map object containing cutout data.
    """

    hdulist = pf.open(fname)
    datalist = []
    hdrlist = []

    for hdu in hdulist[1:]:
        datalist.append(hdu.data)
        hdrlist.append(list(hdu.header.cards))

    #Assume comments for all extensions are the same
    comments = []
    if extract_comments:
        comments = fits_utils.extract_header_comments(hdulist[1].header.cards)

    return map_utils.bundle_cutout(datalist, header=hdrlist, unit_map=unit_map,
                                   comments=comments)


def write_planck_cutout(fname, cutout):
    """ Write a cutout map object to file.

    Arguments:
        fname (string): Filename of the output file.
        cutout (map object): The map object to save.

    Returns:
        None
    """
    datalist = cutout['data']
    cutout = map_utils.sign_map(cutout)
    headerlist = fits_utils.prepare_header(cutout)
    hdulist = [pf.PrimaryHDU()]
    namelist = []
    for header in headerlist:
        for card in header:
            if card[0].startswith('EXTNAME'):
                namelist.append(card[1])
                break
    if namelist == []:
        namelist = [None] * len(headerlist)

    for data, name, header in zip(datalist, namelist, headerlist):
        if isinstance(data, np.ma.masked_array):
            data = np.array(data)
        hdulist.append(pf.ImageHDU(data=data, name=name,
                                   header=pf.Header(header)))
        hdulist = pf.HDUList(hdulist)
    hdulist.writeto(fname, clobber=True)
