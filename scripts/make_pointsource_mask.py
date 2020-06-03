import astropy.io.fits as pf
import numpy as np
import calculation.masking as maskcalc
from utils import map_utils, file_utils, fits_io_utils
import argparse


def load_sources(fname, fetch_columns=[]):
    """ Load the source data of a given catalogue. 

    Fetches the 'GLON' and 'GLAT' columns automatically (as
        one item), and optionally other columns as well.

        Arguments:
        fname: File name of the source catalogue.
        fetch_columns: Which data columns of the file to get, in
            addition to 'GLON' and 'GLAT'.

        Returns: List, whose first element is a numpy array
            containing the 'GLON' and 'GLAT' columns, and whose
            other elements are the columns specified by the user.
    """
    data = pf.open(fname)[1].data
    coords = np.array([data['GLON'], data['GLAT']])
    res = [coords]
    for colname in fetch_columns:
        res.append(data[colname])
    return res


def filter_sources(coords, geq_filter=[], leq_filter=[], flag_filter=[]):
    """Given a list of source coordinates, filters away those that don't
            match the criteria.
        
        Arguments: 
            coords: 2xNsources-sized numpy array, representing 'GLON' and
                'GLAT'.
            geq_filter: list of doublets. Each doublet represents a filter, and
                the first element of each doublet is an Nsources-length list of
                values used in the filtering. The second element is the value
                with which this list will be compared. If the values in the
                list are greater than or equal to the value, they will be
                included.
            leq_filter: Same as geq_filter, but the condition is
                less than or equal.
            flag_filter: Same as geq_filter, but the
                condition is that to be included, the value in the list must be
                True.

            Returns: numpy array of size 2xf, where f is the number of
                remaining sources after filtering, and the logical filter
                itself, which is a f-sized boolean numpy array.  """
    currfilter = np.ones(coords.shape[1], dtype=bool)
    for vals, target in geq_filter:
        currfilter = np.logical_and(currfilter, vals >= target)
    for vals, target in leq_filter:
        currfilter = np.logical_and(currfilter, vals <= target)
    for ffilter in flag_filter: 
        currfilter = np.logical_and(currfilter, ffilter)
    return coords[:, currfilter], currfilter


def mask_from_sources(fname, nside, in_radius=None, filters=[],
                      ordering='ring',
                      amplitude_col=None, noise_col=None,
                      fwhm=None):
    """ Creates a mask array given a source catalogue.

    Arguments:
        fname: filename of the source catalogue.
        nside: Output nside of the mask.
        in_radius: The fixed radius around each source to mask away. If
            None, this will be determined dynamically instead.
        filters: Filters to apply to the source catalogue.
        amplitude_col: If in_radius is None, this is the column to use as
            the 'amplitude' in the dynamic radius calculation.
        noise_col: If in_radius is None, this is the column to use as the
            'noise' in the dynamic radius calculation.
        fwhm: If in_radius is None, this is the FWHM to use in the dynamic
            radius calculation.

        Returns: 12 * nside**2-sized numpy array that is the mask.
    """
    fetch_columns = [] 
    for cfilter in filters:
        filter_type = cfilter['filter_type']
        if filter_type in ('geq_thresh', 'leq_thresh', 'flag_filter'):
            fetch_columns.append(cfilter['filter_col'])
        elif filter_type in ('geq_ratio_thresh', 'leq_ratio_thresh'):
            fetch_columns.append(cfilter['numerator_col'])
            fetch_columns.append(cfilter['denominator_col'])
    if in_radius is None: 
        fetch_columns.append(amplitude_col)
        fetch_columns.append(noise_col)
    if fetch_columns == []:
        res = load_sources(fname)
    else:
        res = load_sources(fname, fetch_columns=fetch_columns)
    coords = res[0]
    kwargs = {}
    i = 1
    geq_filter = []
    leq_filter = []
    flag_filter = []
    for cfilter in filters:
        filter_type = cfilter['filter_type']
        if filter_type == 'geq_thresh':
            geq_filter.append((res[i], cfilter['threshold']))
        elif filter_type == 'leq_thresh':
            leq_filter.append((res[i], cfilter['threshold']))
        elif filter_type == 'geq_ratio_thresh':
            geq_filter.append((res[i] / res[i+1], cfilter['threshold']))
            i += 1
        elif filter_type == 'geq_ratio_thresh':
            leq_filter.append((res[i] / res[i+1], cfilter['threshold']))
            i += 1
        elif filter_type == 'flag_filter':
            flag_filter.append(res[i])
        i += 1
    kwargs['geq_filter'] = geq_filter
    kwargs['leq_filter'] = leq_filter
    kwargs['flag_filter'] = flag_filter

    filtered_src, srcfilter = filter_sources(coords, **kwargs)
    if in_radius is None:
        amplitude = res[i]
        amplitude = amplitude[srcfilter]
        i += 1
        noise = res[i]
        noise = noise[srcfilter]
        radii = maskcalc.calc_snr_dep_radii(amplitude, noise, fwhm)
    else:
        radii = [in_radius] * len(filtered_src[0])

    mask = maskcalc.radii2mask(nside, filtered_src, radii,
                               ordering=ordering)
    return mask


def parse_and_generate_mask(nside, ordering, sources, filters):
    """ Generates a mask based on source catalogues and filters.

    Arguments:
        nside: The nside of the output mask.
        ordering: 'nested' or 'ring', the ordering of the output mask.
        sources (list of dicts): Each element in this list specifies a source
            catalog, along with the radius and radius unit (in the case we're
            using a fixed radius to mask the sources) or the fwhm, amplitude
            column and noise column (in the case we're using a dynamic radius
            to mask the sources). Keys:
                'source_fname': The filename of the source catalogue.
                'radius': For a fixed radius-masking around the sources, this
                    is the value of the radius to mask.
                'radius_unit': For fixed radius-masking. 'degrees',
                    'arcminutes', or 'radians'.
                'fwhm': The full width half max of the map beam. Used in the
                    dynamic radius case.
                'amplitude_column': The column of the source catalogue that
                    contains the flux to be used in radius calculation. Used in
                    the dynamic radius case.
                'noise_column': The column of the source catalogue that
                    contains the uncertainty to be used in the radius
                    calculation. Used in the dynamic radius case.
        filters (list of dicts): Each element in this list specifies a source
            catalogue and an accompanying filter to apply to that catalogue.
            Keys:
                'filter_type': 'geq_thresh', 'leq_thresh', 'geq_ratio_thresh',
                    'leq_ratio_thresh', or 'flag_filter'. Respectively, they
                    filter on sources whose 'filter_col' are 1) greater than
                    'threshold', 2) less than 'threshold', or on sources
                    whose ratio between 'numerator_col' and 'denominator_col'
                    is 3) greater than 'threshold' and 4) less than
                    'threshold', or on sources 5) whose flags in 'filter_col'
                    are not True.
                'threshold': For the filters that require a threshold value,
                    this specifies the threshold value.
                'filter_col': For the filters that require a single column,
                    specifies the name of that column in the source catalogue.
                'numerator_col': For the filters that require a numerator
                    column, specifies the name of that column.
                'denominator_col': For the filters that require a denominator
                    column, specifies the name of that column.
    Returns:
        A map object that has been generated.
    """
    mask = None
    comments = ["Generated point source mask",
                "Source catalogues used: "]
    for i, source_dict in enumerate(sources):
        if source_dict.get('radius', None) is not None:
            gen_type = 'fixed_radius'
        elif source_dict.get('fwhm', None) is not None:
            gen_type = 'dynamic_radius'
        else:
            raise ValueError('Could not detect whether fixed or dynamic radius')
        currfilters = []
        for cfilter in filters:
            if cfilter['catalogue_idx'] == i:
                currfilters.append(cfilter)
        source_fname = source_dict['source_fname']
        comments.append(file_utils.extract_fname(source_fname))
        kwargs = {}
        kwargs['ordering'] = ordering
        kwargs['filters'] = currfilters
        if gen_type == 'fixed_radius':
            radius = source_dict['radius']
            radius_unit = source_dict['radius_unit']
            if radius_unit == 'degrees':
                radius *= np.pi / 180.0
            elif radius_unit == 'arcminutes':
                radius *= np.pi / 180.0 / 60.0
            elif radius_unit != 'radians':
                raise ValueError('Unknown radius unit %s' % radius_unit)
            kwargs['in_radius'] = radius
            comments.append("Masking radius: %0.3f radians" % radius)
        elif gen_type == 'dynamic_radius':
            kwargs['fwhm'] = source_dict['fwhm']
            kwargs['amplitude_col'] = source_dict['amplitude_column']
            kwargs['noise_col'] = source_dict['noise_column']
            comments.append("Dynamic masking radius")
        currmask = mask_from_sources(source_fname, nside, **kwargs)
        if mask is None:
            mask = currmask
        else:
            mask = mask & currmask
    column_units = ['']
    column_properties = {'signal': [0], 'nonconvertable': [0],
                         'nonsquared': [0], 'unitless': [0],
                         'mask': [0]}
    column_names = ['MASK']
    return map_utils.bundle_fullmap([mask], ordering=ordering,
                                    column_properties=column_properties,
                                    column_units=column_units,
                                    column_names=column_names,
                                    comments=comments)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Create a point source mask from a catalogue."
    )
    parser.add_argument(
        'source_fname',
        type=str,
        help='The filename of the source'
    )
    parser.add_argument(
        'mask_fname',
        type=str,
        help='The filename of the output mask'
    )
    parser.add_argument(
        'nside',
        type=int,
        help='The Nside of the output mask'
    )
    parser.add_argument(
        'ordering',
        choices=['ring', 'nested'],
        help='The ordering of the output map'
    )
    parser.add_argument(
        '--radius',
        dest='radius',
        type=float,
        help='The radius around the point source to mask, in arcminutes. Used for fixed radii.'
    )
    parser.add_argument(
        '--fwhm',
        dest='fwhm',
        type=float,
        help='The FWHM of the beam. Used for dynamic radii.'
    )
    parser.add_argument(
        '--amplitude-type',
        dest='amplitude_type',
        choices=['aperflux', 'detflux', 'gauflux', 'psfflux'],
        type=str,
        help='The amplitude type to use in the dynamic radius calculation'
    )
    parser.add_argument(
        '--filter-col',
        dest='filter_col',
        type=str,
        help='The column we want to filter upon. Only required if --geq-thresh and/or --leq-thresh is set.'
    )
    parser.add_argument(
        '--geq-thresh',
        dest='geq_thresh',
        help='Filters away sources whose values in --filter-col is greater than or equal to this value. Optional.'
    )
    parser.add_argument(
        '--leq-thresh',
        dest='leq_thresh',
        help='Filters away sources whose values in --filter-col is less than or equal to this value. Optional.'
    )

    args = parser.parse_args()
    source = {'source_fname': args.source_fname}
    if args.radius is not None:
        source['radius'] = args.radius
        source['radius_unit'] = 'arcminutes'
    elif args.fwhm is not None:
        source['fwhm'] = args.fwhm
        source['amplitude_column'] = args.amplitude_type.upper()
        source['noise_column'] = args.amplitude_type.upper() + '_ERR'
    sources = [source]
    filters = []
    if args.filter_col is not None:
        if args.geq_thresh is not None:
            filters.append({
                'filter_type': 'geq_thresh',
                'threshold': args.geq_thresh,
                'filter_col': args.filter_col})
        if args.leq_thresh is not None:
            filters.append({
                'filter_type': 'leq_thresh',
                'threshold': args.leq_thresh,
                'filter_col': args.filter_col})

    outmask = parse_and_generate_mask(args.nside, args.ordering, sources, filters)
    fits_io_utils.write_planck_fullmap(args.mask_fname, outmask)
