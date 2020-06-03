import numpy as np

DEFAULT_COLUMN_NAMES = {
    'signal_i': 'I_STOKES',
    'signal_q': 'Q_STOKES',
    'signal_u': 'U_STOKES',
    'covariance_ii': 'II',
    'covariance_iq': 'IQ',
    'covariance_iu': 'IU',
    'covariance_qq': 'QQ',
    'covariance_qu': 'QU',
    'covariance_uu': 'UU',
    'rms_i': 'I_RMS',
    'rms_q': 'Q_RMS',
    'rms_u': 'U_RMS',
    'weights_i': 'I_WEIGHTS',
    'weights_q': 'Q_WEIGHTS',
    'weights_u': 'U_WEIGHTS',
    'mask': 'MASK',
    'hits': 'Hits'
}

def get_hdu_header_val(header, inkey, default_value='nf'):
    """ Finds the value associated with a given header key.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        inkey (string): The key whose value we want to find.
        default_value (anything): If key not found, return this instead. If
            this is equal to 'nf', then an exception will be raised if key is
            not found.

    Returns:
        The value belonging to the header key. Note that the value returned
            corresponds to the first occurence of the key in the list.
    """
    for key, value, comment in header:
        if key == inkey:
            return value
    if default_value != 'nf':
        return default_value
    raise ValueError("Header key %s not found" % inkey)


def get_hdu_header_card(header, inkey, default_value='nf'):
    """ Finds the header card containing a given header key.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        inkey (string): The key whose value we want to find.
        default_value (anything): If key not found, return this instead. If
            this is equal to 'nf', then an exception will be raised if key is
            not found.

    Returns:
        The header card containing inkey. Note that the card returned
            corresponds to the first occurence of the key in the list.
    """
    for card in header:
        key = card[0]
        if key == inkey:
            return card
    if default_value != 'nf':
        return default_value
    raise ValueError("Header key %s not found" % inkey)


def add_hdu_header_card(header, card):
    """ Add a card to a header.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        card (tuple): Card to add to the header. The card will be appended at
            the end.

    Returns:
        Input header with card appended to it.
    """
    header.append(card)
    return header


def replace_hdu_header_card(header, card):
    """ Replace card in header containing the same key as the input card.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        card (tuple): Card to replace an existing card in the header. The card
            to be replaced is the unique card containing the same key as the
            input card. If more than one such card is found, a LookupError is
            raised. The input card is inserted in the same position as the
            existing card.

    Returns:
        Input header with the input card replacing the existing one.
    """
    found = False
    for i in range(len(header)):
        if header[i][0] == card[0]:
            if found:
                raise LookupError("There are more than one instance of the "
                                  "key in the header")
            found = True
            idx = i
    header[idx] = card
    return header


def replace_hdu_header_value(header, key, value):
    """ Replace value in a card containing the input key.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        key (string): Key of the card whose value we want to replace.
        value (string): Value to replace an existing value in the appropriate
            card.
    Returns:
        Input header with the input value replacing the value in the card whose
            key equals the input key.
    """
    found = False
    for i in xrange(len(header)):
        if header[i][0] == key:
            if found:
                raise LookupError("There are more than one instance of the "
                                  "key in the header")
            found = True
            idx = i
    orig_card = header[idx]
    new_card = (orig_card[0], value, orig_card[2])
    header[idx] = new_card
    return header


def add_element_to_hdu_header(header, element, idx=None, idx2=None,
                              eltype=None):
    """ A convenience function for adding a card of the most common types to a
            header.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        element (string or tuple): The value of the card to insert.
            Alternatively, if eltype=None, this argument is the entire card to
            insert.
        idx, idx2 (integer): Certain card types needs one or two indices for
            their key. These keywords are for those cards.
        eltype (string or None): If None, this function behaves just like
            add_hdu_header_card, and 'element' is the card to insert.
            Otherwise, it refers to the type of card we want to insert, and can
            take the following values: 'nside', 'ordering', 'comment', 'unit',
            'unit_cutout', 'type', 'format', 'extname', 'ctype', 'equinox',
            'pc', 'crpix', 'crval', 'cdelt', 'lonpole', 'latpole', 'map'. The
            code itself should be enough to understand these types.

    Returns:
        Input header with the the desired card type inserted.
    """
    if header is None:
        header = []
    if eltype == 'nside':
        card = ('NSIDE', element, '')
    elif eltype == 'ordering':
        card = ('ORDERING', element,
                'Pixel ordering scheme, either RING or NESTED')
    elif eltype == 'comment':
        card = ('COMMENT', element, '')
    elif eltype == 'unit':
        card = ('TUNIT%d' % idx, element, 'physical unit of field')
    elif eltype == 'unit_cutout':
        card = ('UNITS', element, 'physical unit of field')
    elif eltype == 'type':
        card = ('TTYPE%d' % idx, element, 'label for field %d' % idx)
    elif eltype == 'format':
        descstring = format_to_descstring(element)
        card = ('TFORM%d' % idx, element, 'data format of field: %s' %
                descstring)
    elif eltype == 'extname':
        card = ("EXTNAME", element, "Original map extension column")
    elif eltype == 'ctype':
        card = ("CTYPE%d" % idx, element, "Coordinate type: %s" % element)
    elif eltype == 'equinox':
        card = ("EQUINOX", element, "Equinox of Ref Coord")
    elif eltype == 'pc':
        card = ("PC%d_%d" % (idx, idx2), element, "Degrees/pixel")
    elif eltype == 'crpix':
        card = ("CRPIX%d" % idx, element, "Reference pixel in x")
    elif eltype == 'crval':
        card = ("CRVAL%d" % idx, element, "Galactic longitude of reference "
                "pixel")
    elif eltype == 'cdelt':
        if idx == 1:
            axis = 'X'
        else:
            axis = 'Y'
        card = ("CDELT%d" % idx, element, "Pixel width in degrees for %s axis"
                % axis)
    elif eltype == 'lonpole':
        card = ("LONPOLE", element, "Galactic longitude of native pole")
    elif eltype == 'latpole':
        card = ("LATPOLE", element, "Galactic latitude of native pole")
    elif eltype == 'map':
        card = ("MAP", element, "Original map")
    elif eltype is None:
        card = element
    header = add_hdu_header_card(header, card)
    return header


def add_elements_to_hdu_header(header, elements, eltype):
    """ Multi-element wrapper to add_element_to_hdu_header, with automatic
        index handling.

    See add_element_to_hdu_header for documentation of how each card is added.
    For each element to be added, an index is passed to
    add_element_to_hdu_header, corresponding to that element's position in the
    list (1-based).

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        elements (list): Each element corresponds to an element argument to
            add_element_to_hdu_header.
        eltype (string or None): see add_element_to_hdu_header.

    Returns:
        Input header with the the desired cards inserted.
    """
    if header is None:
        header = []
    for i, element in enumerate(elements):
        header = add_element_to_hdu_header(header, element, idx=i+1,
                                           eltype=eltype)
    return header


def create_basic_hdu_header(inmap):
    """ Create a basic FITS header based on information in fullmap map object.

    Arguments:
        inmap (map object): A fullmap map object containing the data to write
            to a FITS file.
    
    Returns:
        List of header cards (tuples with three elements: (KEY, VALUE,
            COMMENT)).
    """
    header = []
    nside = inmap['nside']
    header = add_element_to_hdu_header(header, nside, eltype='nside')
    ordering = inmap['ordering'].upper()
    header = add_element_to_hdu_header(header, ordering, eltype='ordering')
    column_names = inmap['column_names']
    header = add_elements_to_hdu_header(header, column_names, 'type')
    unit_list = get_fits_ready_units(inmap)
    header = add_elements_to_hdu_header(header, unit_list, 'unit')
    format_list = numpy2fitsformat(inmap)
    header = add_elements_to_hdu_header(header, format_list, 'format')
    header = add_element_to_hdu_header(
        header, ('PIXTYPE', 'HEALPIX', 'HEALPIX pixelisation'))
    for comment in inmap['comments']:
        header = add_element_to_hdu_header(header, comment, eltype='comment')
    return header


def create_basic_hdu_headerlist(inmap):
    """ Create a list of headers for a FITS cutout based on information in
        cutout map object.

    Arguments:
        inmap (map object): A cutout map object containing the data to write to
            a FITS file.

    Returns:
        List of headers (which again are lists of header cards), one header per
            extension in the FITS file.
    """
    num_map_columns = len(inmap['data'])
    headerlist = []
    lon = inmap['lon']
    lat = inmap['lat']
    psi = inmap['psi']
    size = inmap['size']
    res = inmap['res'] / 60.0
    refpix = (size + 1) * 0.5
    column_names = inmap['column_names']
    unit_list = get_fits_ready_units(inmap)
    common_vals = [("GLON-SIN", 'ctype', 1),
                   ("GLAT-SIN", 'ctype', 2),
                   (2000.0, 'equinox'),
                   (1.0, 'pc', 1, 1),
                   (0.0, 'pc', 2, 1),
                   (0.0, 'pc', 1, 2),
                   (1.0, 'pc', 2, 2),
                   (refpix, 'crpix', 1),
                   (refpix, 'crpix', 2),
                   (lon, 'crval', 1),
                   (lat, 'crval', 2),
                   (-res, 'cdelt', 1),
                   (res, 'cdelt', 2),
                   (180.0 - psi, 'lonpole'),
                   (0.0, 'lonpole')]
    if inmap['orig_mapfname'] is not None:
        common_vals.append((inmap['orig_mapfname'], 'map'))
    for i in xrange(num_map_columns):
        currheader = []
        currheader = add_element_to_hdu_header(currheader, column_names[i],
                                               eltype='extname')
        for common_val in common_vals:
            idx = None
            idx2 = None
            value = common_val[0]
            eltype = common_val[1]
            if len(common_val) >= 3:
                idx = common_val[2]
                if len(common_val) == 4:
                    idx2 = common_val[3]
            currheader = add_element_to_hdu_header(currheader, value,
                                                   eltype=eltype, idx=idx,
                                                   idx2=idx2)
        currheader = add_element_to_hdu_header(currheader, unit_list[i],
                                               eltype='unit_cutout')
        for comment in inmap['comments']:
            currheader = add_element_to_hdu_header(currheader, comment,
                                                   eltype='comment')
        headerlist.append(currheader)
    return headerlist


def guess_fits_column_names(column_properties, num_map_columns):
    """ Based on column properties, makes a best-effort guess to determine the
        FITS name of each column represented.
    
    Arguments:
        column_properties (dict): See README.txt for information.
        num_map_columns (int): The total number of columns to determine.

    Returns:
        List of strings representing the column names of each column.
    """
    fits_colnames = []
    propnames = []
    fields = 'iqu'
    for subtype in ['signal', 'rms', 'weight']:
        propnames.extend([subtype + '_' + field for field in fields])
    for i in xrange(len(fields)):
        for j in xrange(i, len(fields)):
            propnames.append('covariance_' + fields[i] + fields[j])
    propnames.append('mask')
    propnames.append('hits')
    for col in xrange(num_map_columns):
        for propname in propnames:
            if col in column_properties.get(propname, []):
                fits_colnames.append(DEFAULT_COLUMN_NAMES[ propname])
                break
    if len(fits_colnames) != num_map_columns:
        raise ValueError("Not all column names were guessed")
    return fits_colnames


def numpy2fitsformat(inmap):
    """ Generates a list of FITS-style formats given the data in a map object
        and its data types.

    Arguments:
        inmap (map object): Map object for whose data columns we want to
            generate the format list.

    Returns:
        List of strings where each element is the FITS-style format of the
        corresponding data column in inmap.
    """
    # Not exactly the same as the other way around, because 'B' is used as a
    # boolean in Planck
    conv = {np.dtype(np.bool): 'B',
            np.dtype(np.uint8): 'B',
            np.dtype(np.int16): 'I',
            np.dtype(np.int32): 'J',
            np.dtype(np.int64): 'K',
            np.dtype(np.float32): 'E',
            np.dtype(np.float64): 'D',
            np.dtype(np.complex64): 'C',
            np.dtype(np.complex128): 'M'}
    fitsformats = []
    for col in inmap['data']:
        fitsformats.append(conv[col.dtype])
    return fitsformats


def find_hdu_num(hdulist, hdu_name):
    """ Locate a given HDU number.

    Arguments:
        hdulist (list): All HDUs that we want to search.
        hdu_name (string): The EXTNAME of the HDU we want to locate.

    Returns:
        The index of the HDU whose EXTNAME matches hdu_name.
    """
    hdu_num = None
    for i in xrange(len(hdulist)):
        if 'EXTNAME' not in hdulist[i].header:
            continue
        if hdulist[i].header['EXTNAME'] == hdu_name:
            hdu_num = i
            break
    if hdu_num is None:
        raise ValueError('HDU name %s not found in hdu list' % hdu_name)
    return hdu_num


def format_to_descstring(informat):
    """ Gives the description of a specific type of FITS format.

    Arguments:
        informat (string): A FITS-type format (single letter).

    Returns:
        An appropriate description string (matching the Planck style) for that
        format.
    """
    conv = {'B': 'Unsigned 1-byte integer',
            'E': '4-byte REAL',
            'D': '8-byte REAL'}
    return conv[informat]


def resolve_hdu_column_properties(header, unit_map, column_filter=None):
    """ Determines the column properties of FITS full map columns based on
        header information.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        column_filter (None or list of integers): which columns to include in
            the calculation. If None, all columns will be included.

    Returns:
        dict containing the column properties as described in README.txt
    """
    numcols = get_hdu_header_val(header, 'TFIELDS')
    colprops = {}
    if column_filter is None:
        column_filter = range(numcols)
    col_idx = 0
    for i in xrange(1, numcols + 1):
        if i - 1 not in column_filter:
            continue
        typecard = get_hdu_header_card(header, 'TTYPE%d' % i)
        unitcard = get_hdu_header_card(header, 'TUNIT%d' % i,
                                       default_value=None)
        formatcard = get_hdu_header_card(header, 'TFORM%d' % i)
        currtype = typecard[1]
        if unitcard is not None:
            currunit = backend_defaults.get_backend_unit(unitcard[1], unit_map)
        else:
            currunit = None
        currformat = formatcard[1]
        currcol_properties = backend_defaults.resolve_properties(
            currtype, currunit, informat=currformat)
        if not currcol_properties:
            raise ValueError("Unresolvable column found, column no. %d" % i)
        for ccproperty in currcol_properties:
            if colprops.get(ccproperty, None) is not None:
                colprops[ccproperty].append(col_idx)
            else:
                colprops[ccproperty] = [col_idx]
        col_idx += 1
    return colprops


def resolve_hdulist_column_properties(header, unit_map, column_filter=None):
    """ Determines the column properties of FITS cutout columns based on
        header information.

    Arguments:
        header (list of headers): List of headers, each of which belongs to a
            specific cutout column.
        column_filter (None or list of integers): which columns to include in
            the calculation. If None, all columns will be included.

    Returns:
        dict containing the column properties as described in README.txt
    """
    numcols = len(header)
    if column_filter is None:
        column_filter = range(numcols)
    colprops = {}
    col_idx = 0
    for i in xrange(1, numcols + 1):
        if i - 1 not in column_filter:
            continue
        currtype = get_hdu_header_val(header[i], 'EXTNAME')
        currunit = backend_defaults.get_backend_unit(
            get_hdu_header_val(header[i], 'UNITS'), unit_map)
        currcol_properties = backend_defaults.resolve_properties(currtype,
                                                                 currunit)
        if not currcol_properties:
            raise ValueError("Unresolvable column found, column no. %d" % i)
        for ccproperty in currcol_properties:
            if ccproperty in colprops:
                colprops[ccproperty].append(col_idx)
            else:
                colprops[ccproperty] = [col_idx]
        col_idx += 1
    return colprops


def resolve_hdu_column_units(header, unit_map, column_filter=None):
    """ Determines the units of FITS fullmap columns based on header
        information. 

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        column_filter (None or list of integers): which columns to include in
            the calculation. If None, all columns will be included.

    Returns:
        A list where each element contains the internal unit of the
            corresponding map column.
    """
    numcols = get_hdu_header_val(header, 'TFIELDS')
    if column_filter is None:
        column_filter = range(numcols)
    colunits = []
    for i in xrange(1, numcols + 1):
        if i-1 not in column_filter:
            continue
        value = get_hdu_header_val(header, 'TUNIT%d' % i, default_value='')
        colunits.append(backend_defaults.get_backend_unit(value, unit_map))
    return colunits


def resolve_hdulist_column_units(header, unit_map, column_filter=None):
    """ Determines the units of FITS cutout columns based on header
        information. 

    Arguments:
        header (list of headers): List of headers, each of which belongs to a
            specific cutout column.
        column_filter (None or list of integers): which columns to include in
            the calculation. If None, all columns will be included.

    Returns:
        A list where each element contains the internal unit of the
            corresponding map column.
    """

    numcols = len(header)
    if column_filter is None:
        column_filter = range(numcols)
    colunits = []
    for i in xrange(1, numcols + 1):
        if i-1 not in column_filter:
            continue
        colunits.append(
            backend_defaults.get_backend_unit(
                get_hdu_header_val(header[i], 'UNITS'), unit_map))
    return colunits


def extract_hdu_column_types(header, column_filter=None):
    """ Determines the type of FITS fullmap columns based on header
        information.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)).
        column_filter (None or list of integers): which columns to include in
            the calculation. If None, all columns will be included.

    Returns:
        A list where each element contains the FITS type of the corresponding
            map column.
    """
    numcols = get_hdu_header_val(header, 'TFIELDS')
    if column_filter is None:
        column_filter = range(numcols)
    coltypes = []
    for i in xrange(1, numcols + 1):
        if i-1 not in column_filter:
            continue
        value = get_hdu_header_val(header, 'TTYPE%d' % i)
        coltypes.append(value)
    return coltypes


def extract_hdulist_column_types(header, column_filter=None):
    """ Determines the type of FITS cutout columns based on header
        information.

    Arguments:
        header (list of headers): List of headers, each of which belongs to a
            specific cutout column.
        column_filter (None or list of integers): which columns to include in
            the calculation. If None, all columns will be included.

    Returns:
        A list where each element contains the FITS type of the corresponding
            map column.
    """
    numcols = len(header)
    if column_filter is None:
        column_filter = range(numcols)
    coltypes = []
    for i in xrange(1, numcols + 1):
        if i-1 not in column_filter:
            continue
        value = get_hdu_header_val(header[i], 'EXTNAME')
        coltypes.append(value)
    return coltypes


def extract_header_comments(header):
    """ Get all comments from a FITS header.

    Arguments:
        header (list of tuples): Each element is a header card in the same way
            pyfits treats them (triplet of (KEY, VALUE, COMMENT)). (Note that
            for this function, 'comments' refers to the VALUEs of those cards
            whose KEY is 'COMMENT', not the COMMENT field of each card).

    Returns:
        A list of the values of all header cards whose KEY is 'COMMENT'.
    """
    comments = []
    for key, value, cardcomment in header:
        if key == 'COMMENT':
            comments.append(value)
    return comments


def fits2numpyformat(format_string):
    """ Convert from FITS format strings to numpy data types.

    Arguments:
        format_string (string): A FITS format string (single character).

    Returns:
        the numpy datatype corresponding to the format string.
    """
    conv = {'L': np.dtype(np.bool),
            'B': np.dtype(np.uint8),
            'I': np.dtype(np.int16),
            'J': np.dtype(np.int32),
            'K': np.dtype(np.int64),
            'E': np.dtype(np.float32),
            'D': np.dtype(np.float64),
            'C': np.dtype(np.complex64),
            'M': np.dtype(np.complex128)}
    return conv[format_string]


def prepare_header(inmap):
    "Wrapper to prepare_fullmap_header and prepare_cutout_header_list."
    if inmap['type'] == 'fullmap':
        return prepare_fullmap_header(inmap)
    elif inmap['type'] == 'cutout':
        return prepare_cutout_header_list(inmap)


def prepare_fullmap_header(inmap):
    """ Make a FITS header based on fullmap map object information.

    The header is created based on the information in the map object, and
    includes any comments that might be there.

    Arguments:
        inmap (map object): The full map from which to create a FITS header.

    Returns:
        A list of header cards, representing the FITS header.
    """
    nheader = create_basic_hdu_header(inmap)
    return nheader


def prepare_cutout_header_list(inmap):
    """ Make a FITS header list based on cutout map object information.

    The header list is created based on the information in the map object, and
    includes any comments that might be there.

    Each element in the final list is a header, meant to be assigned to a
    specific extension in the FITS file. This is since for cutouts each column
    has its own extension.

    Arguments:
        inmap (map object): The cutout from which to create the header list.

    Returns:
        A list of lists of header cards, each list representing a FITS header.
    """

    nheaderlist = create_basic_hdu_headerlist(inmap)
    return nheaderlist


def get_fits_ready_units(inmap):
    """ Create a list of FITS-formatted units corresponding to the columns in a
        map.

    Arguments:
        inmap (map object): The full map whose columns need units.

    Returns:
        A list of strings, where each element is the FITS formatted unit
            of the corresponding column.
    """
    col_units = inmap['column_units']
    col_properties = inmap['column_properties']
    out_units = []
    for i, currunit in enumerate(col_units):
        if i in col_properties.get('squared', []):
            currunit = currunit[:-2]
        if i in col_properties.get('unitless', []):
            out_units.append('')
            continue
        if currunit.endswith('kcmb'):
            base = 'K_CMB'
            sep = 'kcmb'
        elif currunit.endswith('jysr'):
            base = 'jy/sr'
            sep = 'jysr'
        elif currunit.endswith('krj'):
            base = 'K_RJ'
            sep = 'krj'
        elif currunit.endswith('ysz'):
            base = 'y_SZ'
            sep = 'ysz'
        else:
            raise ValueError("Unrecognized unit %s" % currunit)
        prefix = currunit.split(sep)[0]
        unit = prefix + base
        if i in col_properties.get('squared', []):
            unit = '(' + unit + ')^2'
        out_units.append(unit)
    return out_units
