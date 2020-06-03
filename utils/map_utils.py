from utils import fits_utils
import copy
import numpy as np


def bundle_fullmap(data, default_metadata={}, ordering=None, header=None,
                   column_properties=None, column_units=None,
                   column_names=None, comments=[], header_filter=None,
                   unit_map=None, metadata_filter=None):

    """ Creates a bona fide fullmap object (a dict) to be used internally.

    Arguments:
        data (list/numpy array of shape (n, npix) or (npix)): The data columns
            of the map.
        default_metadata (dict): The metadata which will be used for the map
            unless overridden by the other arguments. This can typically be the
            previous version of the map file.
        ordering (string): 'ring' or 'nested'. Overrides value in
            default_metadata and header.
        header (list of tuples): The header (typically of a FITS file) to be
            used as basis for the metadata of the output map. Will be
            overridden by the corresponding fields in default_metadata (i.e.
            this header has the lowest priority when populating the metadata of
            the new map). Comments from this header are never used.
        column_properties (dict of string->list of ints): The mapping from a
            property to specific column numbers (see README.txt for a more
            in-depth explanation). Overrides default_metadata.
        column_units (list of strings): The units belonging to the
            corresponding column. Overrides default_metadata.
        column_names (list of strings): The names of the corresponding FITS
            columns. Overrides default_metadata.
        comments (list of strings): Each element is a 'comment' field for the
            map header. Overrides default_metadata.
        header_filter (list of ints): Provides a possibility to not use all
            data in the 'header' argument. If the 'data' argument contains,
            say, 3 columns and the header provides info for 7, you can pass a
            list of 3 ints in the header_filter argument, specifying which of
            the 7 columns specified by the header you want to be included in
            the new map object.
        metadata_filter (list of ints): This provides the same functionality as
            the header_filter, but applied to default_metadata.

    Returns:
        a dict representing the fullmap object described in README.txt

    """

    if len(data) > 100:
        data = [data]
    num_map_columns = len(data)
    if header_filter is None:
        header_filter = range(num_map_columns)
    elif len(header_filter) != num_map_columns:
        raise ValueError("Column filter and number of map columns are not "
                         "equal")
    if header is None:
        header = default_metadata.get('orig_header', None)
    if ordering is None:
        ordering = default_metadata.get(
            'ordering', None)
        if ordering is None:
            ordering = fits_utils.get_hdu_header_val(
                header, 'ORDERING').lower()
    nside = int(np.sqrt(len(data[0]) / 12))
    if column_properties is None:
        column_properties = default_metadata.get(
            'column_properties', None)
        if column_properties is None:
            column_properties = fits_utils.resolve_hdu_column_properties(
                header, unit_map, header_filter)
    if column_properties is not None and metadata_filter is not None:
        colprops_old = copy.deepcopy(column_properties)
        column_properties = {}
        for key, columns in colprops_old.iteritems():
            newcols = []
            count = 0
            for col in metadata_filter:
                if col in columns:
                    newcols.append(count)
                count += 1

            column_properties[key] = newcols

    if column_units is None:
        column_units = default_metadata.get(
            'column_units', None)
        if column_units is None:
            column_units = fits_utils.resolve_hdu_column_units(
                header, unit_map, header_filter)

    if column_units is not None and metadata_filter is not None:
        column_units = [column_units[i] for i in
                        range(len(column_units)) if i in
                        metadata_filter]
           
    if len(column_units) != len(data):
        raise ValueError("Length of data is not equal to length of column units")
    filename = default_metadata.get('filename', None)
    if filename is None and header is not None:
        filename = fits_utils.get_hdu_header_val(header, 'FILENAME',
                                                 default_value=None)
    if comments == []:
        comments = default_metadata.get('comments', [])
    if column_names is None:
        column_names = default_metadata.get(
            'column_names', None)
        if column_names is None:
            if header is None:
                column_names = fits_utils.guess_fits_column_names(
                    column_properties, num_map_columns)
            else:
                column_names = fits_utils.extract_hdu_column_types(
                    header, header_filter)
    if column_names is not None and metadata_filter is not None:
        column_names = [column_names[i] for i in 
                        range(len(column_names)) if i in
                        metadata_filter]
    k = 2
    repeat = True
    while repeat:
        repeat = False
        for i in range(len(column_names)-1):
            for j in range(i+1, len(column_names)):
                if column_names[i] == column_names[j]:
                    column_names[j] = column_names[j] + '_%d' % k
                    repeat = True
    if len(column_names) != len(data):
        raise ValueError("Length of data is not equal to length of column "
                         "names")
    return {'data': data, 'orig_header': header, 'type': 'fullmap', 
            'nside': nside, 'column_properties': column_properties,
            'ordering': ordering, 'column_units': column_units, 
            'comments': comments, 'filename': filename, 'column_names':
            column_names, 'orig_header_filter': header_filter}


def bundle_cutout(data, default_metadata={}, header=None,
                  column_properties=None, column_units=None, column_names=None,
                  size=None, lon=None, lat=None, psi=None, res=None,
                  orig_mapfname=None, comments=[], header_filter=None,
                  unit_map=None):

    """ Creates a cutout map object (a dict) to be used internally.

    Arguments:
        data (list/numpy array of shape (n, npix) or (npix)): The data columns
            of the map.
        default_metadata (dict): The metadata which will be used for the map
            unless overridden by the other arguments. This can typically be the
            previous version of the map file.
        header (list of list of tuples): The header (typically of a FITS file)
            to be used as basis for the metadata of the output map. Will be
            overridden by the corresponding fields in default_metadata (i.e.
            this header has the lowest priority when populating the metadata of
            the new map). Comments from this header are never used.
        column_properties (dict of string->list of ints): The mapping from a
            property to specific column numbers (see README.txt for a more
            in-depth explanation). Overrides default_metadata.
        column_units (list of strings): The units belonging to the
            corresponding column. Overrides default_metadata.
        column_names (list of strings): The names of the corresponding FITS
            columns. Overrides default_metadata.
        size (int): The size of the cutout, measured in pixels. Overrides
            default_metadata.
        lon (float): The longitude of the map center, in degrees and galactic
            coordinates. Overrides default_metadata.
        lat (float): The latitude of the map center, in degrees and galactic
            coordinates. Overrides default_metadata.
        psi (float): The rotation, in degrees, of the cutout center relative to
            its original orientation. Overrides default_metadata.
        res (float): The resolution (size of each pixel). Overrides
            default_metadata.
        orig_mapfname (string): The file name of the full map from which the
            cutout was made. Overrides default_metadata.
        comments (list of strings): Each element is a 'comment' field for the
            map header. Overrides default_metadata.
        header_filter (list of ints): Provides a possibility to not use all
            data in the 'header' argument. If the 'data' argument contains,
            say, 3 columns and the header provides info for 7, you can pass a
            list of 3 ints in the header_filter argument, specifying which of
            the 7 columns specified by the header you want to be included in
            the new map object.

    Returns:
        a dict representing the cutout map object described in README.txt

    """

    # Res in arcminutes, lon, lat, psi in degrees. Size in pixels per edge
    if len(data) > 100:
        data = [data]
    num_map_columns = len(data)
    if header_filter is None:
        header_filter = range(num_map_columns)
    elif len(header_filter) != num_map_columns:
        raise ValueError("Column filter and number of map columns are not "
                         "equal")
    if column_properties is None:
        column_properties = default_metadata.get(
            'column_properties', None)
        if column_properties is None:
            column_properties = fits_utils.resolve_hdulist_column_properties(
                header, unit_map, header_filter)
    if column_units is None:
        column_units = default_metadata.get(
            'column_units', None)
        if column_units is None:
            column_units = fits_utils.resolve_hdulist_column_units(
                header, unit_map, header_filter)
    if len(column_units) != len(data):
        raise ValueError("Length of data is not equal to "
                         "length of column units")
    if size is None:
        size = default_metadata.get(
            'size', None)
        if size is None:
            size = fits_utils.get_hdu_header_val(header[0], 'NAXIS1')
    if lon is None:
        lon = default_metadata.get(
            'lon', None)
        if lon is None:
            lon = fits_utils.get_hdu_header_val(header[0], 'CRVAL1')
    if lat is None:
        lat = default_metadata.get(
            'lat', None)
        if lat is None:
            fits_utils.get_hdu_header_val(header[0], 'CRVAL2')
    if psi is None:
        psi = default_metadata.get(
            'psi', None)
        if psi is None:
            psi = 180.0 - fits_utils.get_hdu_header_val(header[0], 'LONPOLE')
    if res is None:
        res = default_metadata.get(
            'res', None)
        if res is None:
            res = (
                abs(fits_utils.get_hdu_header_val(header[0], 'CDELT1')) * 60.0)
    if orig_mapfname is None:
        orig_mapfname = default_metadata.get(
            'orig_mapfname', None)
        if orig_mapfname is None and header is not None:
            orig_mapfname = fits_utils.get_hdu_header_val(header[0], 'MAP',
                                                          default_value=None)
    if comments == []:
        comments = default_metadata.get('comments', [])
    if column_names is None:
        column_names = default_metadata.get(
            'column_names', None)
        if column_names is None:
            if header is None:
                column_names = fits_utils.guess_fits_column_names(
                    column_properties, num_map_columns)
            else:
                column_names = fits_utils.extract_hdulist_column_types(
                    header, header_filter)
    if len(column_names) != len(data):
        raise ValueError("Length of data is not equal to length of column "
                         "names")

    return {'data': data, 'orig_header': header, 'type': 'cutout',
            'column_properties': column_properties, 'size': size, 'lon': lon,
            'lat': lat, 'psi': psi, 'res': res, 'column_units': column_units,
            'comments': comments, 'orig_mapfname': orig_mapfname,
            'column_names': column_names, 'orig_header_filter': header_filter}


def sign_map(fmap, job_id=None):

    """ Utility function for having a uniform way of signing a map with a job
        ID.

    Adds the job ID to the comments along with an indication this was made by
    PLAAVI.

    Arguments:
        fmap (dict): The map object to sign.
        job_id (string): The job id that created the map.

    Returns:
        The signed map object.

    """

    fmap['comments'].insert(0, 'Created by PLAAVI')
    if job_id is not None:
        # Do not change the 'PLAAVI job id:' without notifying the middleware!
        fmap['comments'].insert(1, 'PLAAVI job id: %s' % job_id)
    return fmap
