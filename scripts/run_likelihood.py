import argparse
import subprocess
import glob
import os
import fileinput
import random
import camb
import numpy as np


def process_parameter_file(base_parameter_file, target_parameter_file, new_parameter_dict={}):
    filestring = ''
    with open(base_parameter_file, 'r') as f:
        line = f.readline()
        while line:
            currline = line
            for parameter, value in new_parameter_dict.items():
                if line.startswith(parameter + ' '):
                    padding = 30
                    if len(parameter) >= 30:
                        padding = 38
                    currline = '{0:<{1}}= {2}\n'.format(parameter, padding, value)
                    break
            filestring += currline
            line = f.readline()

    with open(target_parameter_file, 'w') as f:
        f.write(filestring)
        f.truncate()


class StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        param_dict = {}
        for kv in values.split(","):
            k, v = kv.split("=")
            start, end, step = v.split(":")
            param_dict[k] = [float(start), float(end), float(step)]
        setattr(namespace, self.dest, param_dict)


def run_command(command):
    print(command)
    process = subprocess.Popen(
        command,
        stdout = subprocess.PIPE,
        stdin=subprocess.PIPE)
    for stdout_line in process.stdout:
        print(stdout_line.decode(), end='')
    del process
    return


def param_recursor(param_range, executor, updater, init_metadata):

    curr_meta = init_metadata
    curr_param_range_dict = param_range.copy()

    def recurse_params(curr_param_dict, curr_metadata):
        if curr_param_dict == {}:
            curr_metadata = executor(curr_metadata)
            return curr_metadata
        key, value = curr_param_dict.popitem()
        print(value)
        numsteps = round((value[1] - value[0]) / value[2]) + 1
        for val in np.linspace(value[0], value[1], num=numsteps):
            curr_metadata = updater(curr_metadata, key, val)
            curr_metadata = recurse_params(curr_param_dict.copy(), curr_metadata)
        return curr_metadata
    return recurse_params(curr_param_range_dict, curr_meta)


def map_likelihood(
        base_camb_param_file, base_info_file, target_dir,
        param_range, label, lmin, lmax, like_file,
        enabled_spectra=['TT', 'TE', 'TB', 'EE', 'EB', 'BB']):
    metadata = {}
    metadata['model'] = camb.read_ini(base_camb_param_file)
    metadata['base_cl_prefix'] = target_dir + 'cls_' + label
    metadata['currparam'] = []
    metadata['start_clfile'] = None

    def execute(curr_metadata):
        results = camb.get_results(curr_metadata['model'])
        cls = results.get_total_cls(CMB_unit='muK')
        ells = np.arange(len(cls)).reshape(len(cls), 1)
        cls = np.append(ells, cls, axis=1)
        parstring = curr_metadata['currparam'][0] + str(curr_metadata['currparam'][1])
        clfname = curr_metadata['base_cl_prefix'] + '_' + parstring + '.dat'
        np.savetxt(clfname, cls)
        if curr_metadata['start_clfile'] is None:
            curr_metadata['start_clfile'] = clfname
        curr_metadata['cl_filelist'].write(str(curr_metadata['currparam'][1]) + ' ' + clfname.split('/')[-1] + '\n')
        return curr_metadata

    def update(curr_metadata, par_name, par_val):
            namelist = par_name.split('.')
            namelist.reverse()
            model = curr_metadata['model']
            currobj = model
            currname = namelist[-1]
            while len(namelist) > 1:
                currobj = getattr(currobj, namelist.pop())
                currname = namelist[-1]
            setattr(currobj, currname, par_val)
            curr_metadata['model'] = model
            curr_metadata['currparam'] = [currname, par_val]
            return curr_metadata

    cllist_name = target_dir + 'cllist_' + label + '.dat'
    with open(cllist_name, 'w') as cllistfile:
        metadata['cl_filelist'] = cllistfile
        metadata = param_recursor(param_range, execute, update, metadata)

    commlike = '/mn/stornext/u3/eirikgje/src/Commander/commander1/src/comm_process_resfiles/comm_like_tools'
    base_info_file = target_dir + base_info_file + '.txt'
    curr_info_file = target_dir + 'info_' + label + '.txt'
    process_parameter_file(
        base_info_file, curr_info_file,
        new_parameter_dict={
            'DATAFILE': like_file})
    spectra = ['TT', 'TE', 'TB', 'EE', 'EB', 'BB']
    spectrum_flags = ['t' if spec in enabled_spectra else 'f' for spec in spectra]

    run_command([commlike, 'fast_par_estimation', curr_info_file,
                 metadata['start_clfile'], cllist_name, str(lmin), str(lmax)] + spectrum_flags + ['.true.', target_dir + label + '_likelihood.dat'])


def run_likelihood(data_dir,
                   base_camb_param_file,
                   param_range,
                   likelihood_type,
                   label,
                   base_info_file,
                   lmin,
                   lmax,
                   run_name,
                   base_data_dir='/mn/stornext/d16/cmbco/eirikgje/data/',
                   create_data=False,
                   mask_file=None,
                   nside=None,
                   full_cov=False,
                   beam_file=None,
                   fiducial_cl_file=None):
    currdir = os.getcwd()
    data_dir = base_data_dir + data_dir + '/'
    os.chdir(data_dir)
    base_camb_file = data_dir + base_camb_param_file

    if create_data:
        commproc = '/mn/stornext/u3/eirikgje/src/Commander/commander1/src/comm_process_resfiles/comm_process_resfiles'
        scalapost = '/mn/stornext/u3/hke/owl/quiet_svn/oslo/src/f90/scalapost/scalapost'
        commlike = '/mn/stornext/u3/eirikgje/src/Commander/commander1/src/comm_process_resfiles/comm_like_tools'
        mask_file = data_dir + mask_file
        beam_file = data_dir + beam_file
        fiducial_cl_file = data_dir + fiducial_cl_file
        chain_dir = data_dir + 'chains_' + run_name + '/'
        num_samples = len(glob.glob(chain_dir + 'chisq_c0001_*'))
        file_list = glob.glob(chain_dir + 'chain_fg_amps_*')
        burnin = num_samples / 2
        random_seed = random.randint(0, 999999)
        run_command([commproc, 'pix2mean_cov', chain_dir + label,
                     str(nside), '3', '1', '3', '3', str(burnin),
                     '0', '0', str(random_seed), '.true.',
                     mask_file] + file_list)
        run_command([scalapost, 'rms2cov',
                     chain_dir + label+'_rms.fits', '1.',
                     chain_dir + label+'_rms_N.unf'])
        run_command([commlike, 'mapcov2gausslike',
                     chain_dir + label + '_mean.fits',
                     mask_file,
#                     chain_dir + label + '_rms_N.unf',
                     chain_dir + label + '_N.unf',
                     '.true.', beam_file, fiducial_cl_file,
                     '47', '0', '47', 'eigen_StoN', '1e-13',
                     '1e-13', '1.', '0', '0', str(random_seed+1), 'gausslike_' + label])
    map_likelihood(base_camb_file, base_info_file, data_dir, param_range, label, lmin, lmax, 'gausslike_' + label + '.fits',
                   enabled_spectra=['TE', 'EE'])

    os.chdir(currdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run likelihoods based on Commander samples")
    parser.add_argument(
        'data_dir',
        type=str,
        help='The directory (relative to the base data directory) where the Commander samples will be found, and where everything will be created.')
    parser.add_argument(
        'base_camb_param_file',
        type=str,
        help='The CAMB parameter file (relative to the base data directory) that will be modified for each run.'
    )
    parser.add_argument(
        '--set_parameter_ranges',
        dest='param_range',
        action=StoreDictKeyPair,
        metavar="KEY1=START1:END1:STEP1,KEY2=START2:END2:STEP2...",
        help='The CAMB parameters to vary for the likelihood evaluation'
    )
    parser.add_argument(
        'likelihood_type',
        type=str,
        help='Which likelihood to use. Currently supported: gausslike'
    )
    parser.add_argument(
        'label',
        type=str,
        help='The label to be used for the likelihood data'
    )
    parser.add_argument(
        'base_info_file',
        type=str,
        help='The base info-file used for the likelihood evaluation'
    )
    parser.add_argument(
        'lmin',
        type=int,
        help='The l_min used for the likelihood evaluation'
    )
    parser.add_argument(
        'lmax',
        type=int,
        help='The l_max used for the likelihood evaluation'
    )
    parser.add_argument(
        '-nside',
        dest='nside',
        help='The nside of the maps. Only needed if --create-data is set.'
    )
    parser.add_argument(
        '-mask-file',
        type=str,
        dest='mask_file',
        help='The name of the mask file used (relative to the base data directory). Only needed if --create-data is set.')
    parser.add_argument(
        '-fiducial-cl-file',
        type=str,
        dest='fiducial_cl_file',
        help='The name of the fiducial cl file to be used for gausslike (relative to the base data directory). Only needed if --create-data is set.')

    parser.add_argument(
        '-beam-file',
        type=str,
        dest='beam_file',
        help='The name of the beam file used (relative to the base data directory). Only needed if --create-data is set.')
    parser.add_argument(
        '--create-data',
        dest='create_data',
        action='store_true',
        help='Run the process of creating the likelihood data (matrices etc.) Only necessary for the first run.'
    )
    parser.add_argument(
        'run_name',
        type=str,
        help='The name of the Commander run.'
    )
    parser.add_argument(
        '--full-cov',
        action='store_true',
        dest='full_cov',
        help='Whether to run the likelihood with the full covariance matrix. Alternatively, only the diagonal rms elements are used. Only needed if likelihood_type is gausslike.'
    )

    args = parser.parse_args()
    create_data = True if args.create_data else False
    full_cov = True if args.full_cov else False
    run_likelihood(args.data_dir, args.base_camb_param_file,
                   args.param_range, args.likelihood_type,
                   args.label,
                   args.base_info_file,
                   args.lmin,
                   args.lmax,
                   args.run_name,
                   create_data=create_data,
                   mask_file=args.mask_file,
                   nside=args.nside,
                   full_cov=full_cov,
                   beam_file=args.beam_file,
                   fiducial_cl_file=args.fiducial_cl_file)
