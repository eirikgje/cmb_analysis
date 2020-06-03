import file_utils
import external_exec_utils
import paths
import os
import argparse
import shutil

def diagonalize_matrix(cov_fname, map2mask_fname, out_covname):
    tempfname = 'temprms.fits'
    arguments = 'cov2rms {} {} {}'.format(
        cov_fname, map2mask_fname, tempfname).split(' ')
    external_exec_utils.run_external_process(paths.SCALAPOST_PATH,
                                             arguments)

    arguments = 'rms2cov {} 1. {}'.format(
        tempfname, out_covname).split(' ')
    external_exec_utils.run_external_process(paths.SCALAPOST_PATH,
                                             arguments)
    os.remove(tempfname)


def create_matrix_suite(input_matrix, map2mask, prefix, postfix,
                        num_processes=1):

    inv_fname = '{}covmat_invN_{}.unf'.format(
        prefix, postfix)
    arguments = 'invert LU {} {}'.format(
        input_matrix, inv_fname).split(' ')
    external_exec_utils.run_external_process(
        paths.SCALAPOST_PATH, arguments, is_mpi=True,
        num_processes=num_processes)
    sqrtinvfname = '{}covmat_sqrt_invN_{}.unf'.format(prefix, postfix)
    arguments = 'sqrt {} tmp'.format(inv_fname).split(' ')
    external_exec_utils.run_external_process(
        paths.SCALAPOST_PATH, arguments, is_mpi=True,
        num_processes=num_processes
    )
    shutil.move('tmp_sqrt_inv_N.unf', sqrtinvfname)
    rmsfname = '{}covmat_rms_{}.fits'.format(prefix, postfix)
    arguments = 'cov2rms {} {} {}'.format(input_matrix,
                                          map2mask, rmsfname).split(' ')
    external_exec_utils.run_external_process(
        paths.SCALAPOST_PATH, arguments, is_mpi=True,
        num_processes=num_processes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Use scalapost to create a diagonal matrix (in unf form) using the diagonal elements of a full covariance matrix, as well as creating the inverse, sqrt and rms of this diagonal matrix. Supports looping over several variational strings (for example, 30 GHz, 44 GHz, etc.). The input filename should be of the form {prefix}{variational parameter}{postfix}.unf. The output filenames will be of the form {prefix}diagonal_covmat_{N,invN, sqrt_invN,rms}_{midfix}_{variational parameter}_{postfix}.{unf, fits}, where 'fits' is used for the rms and 'unf' for the full matrices."
    )
    parser.add_argument(
        'data_dir',
        type=str,
        help='The directory where the input matrix is and output matrix will be located.'
    )
    parser.add_argument(
        '--input_prefix',
        dest='input_prefix',
        type=str,
        default='',
        help='The prefix to the input covariance matrix file.')
    parser.add_argument(
        '--input_postfix',
        dest='input_postfix',
        type=str,
        default='',
        help='The postfix to the input covariance matrix file.')
    parser.add_argument(
        'map2mask',
        type=str,
        help='The path to the map2mask to be used.'
    )
    parser.add_argument(
        '--output_prefix',
        dest='output_prefix',
        type=str,
        default='',
        help='The prefix to prepend before the output matrix filenames.'
    )
    parser.add_argument(
        '--output_midfix',
        dest='output_midfix',
        type=str,
        default='',
        help='The midfix string (see description)'
    )
    parser.add_argument(
        '--output_postfix',
        dest='output_postfix',
        default='',
        type=str,
        help='The postfix string (see description)'
    )
    parser.add_argument(
        '--variational_argument',
        dest='variational_argument',
        nargs='*',
        type=str,
        help='List of strings that will be inserted in the input and output filenames, when looping over several matrices (see description)'
    )
    parser.add_argument(
        '--num_processes',
        dest='num_processes',
        default=1,
        type=int,
        help='Number of MPI processes (default 1)'
    )
    args = parser.parse_args()
    varlist = args.variational_argument
    prefix = args.data_dir + args.output_prefix + 'diagonal_'
    for el in varlist:
        input_matrix = '{}{}{}.unf'.format(args.data_dir + args.input_prefix, el, args.input_postfix)
        postfix = '{}_{}_{}'.format(args.output_midfix, el, args.output_postfix)
        N_fname = '{}covmat_N_{}.unf'.format(prefix, postfix)
        diagonalize_matrix(
            input_matrix, args.data_dir + args.map2mask, N_fname)
        create_matrix_suite(N_fname, args.data_dir + args.map2mask, prefix, postfix, args.num_processes)
