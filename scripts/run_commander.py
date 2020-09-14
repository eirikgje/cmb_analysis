#!/mn/stornext/u3/eirikgje/Envs/genan/bin/python

import argparse
import subprocess
import os
import shutil
import random


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


def read_parameter_file(parameter_file):
    """ Returns parameter file as a dict """

    params = {}
    with open(parameter_file, 'r') as f:
        line = f.readline()
        while line:
            currline = line
            if line.startswith('#') or line.startswith('*') or line.strip() == '':
                line = f.readline()
                continue
            k, v = line.split("=")[:2]
            k = k.strip()
            v = v.strip().split(' ')[0]
            params[k] = v
            line = f.readline()
    return params


class StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        param_dict = {}
        for kv in values.split(","):
            k, v = kv.split("=")
            param_dict[k] = v
        setattr(namespace, self.dest, param_dict)

def run_commander(data_dir, run_name, num_processes,
                  param_dict={},
                  base_data_dir='/mn/stornext/u3/eirikgje/data/',
                  change_seed=True,
                  delete_existing_dir=False,
                  commander1=True,
                  machinefile='',
                  build=None,
                  base_param_file=None,
                  single_band=None,
                  single_comp=None):
    data_dir = base_data_dir + data_dir + '/'
    chain_dir = data_dir + 'chains_' + run_name + '/'
    if delete_existing_dir and os.path.isdir(chain_dir):
        shutil.rmtree(chain_dir)
    os.mkdir(chain_dir)
    if commander1:
        exec_path = '/mn/stornext/u3/eirikgje/src/Commander/commander1/src/commander/commander'
        params = {'CHAIN_DIRECTORY': '\'' + chain_dir + '\''}
    else:
        exec_path = '/mn/stornext/u3/eirikgje/src/Commander/' + build + '/bin/commander3'
        params = {'OUTPUT_DIRECTORY':'\'' + chain_dir + '\''}

    param_file_name = 'param_commander_' + run_name + '.txt'
    slurm_name = chain_dir + 'slurm_' + run_name + '.txt'
    errlog_name = chain_dir + 'errors_' + run_name + '.txt'

    if machinefile == '' or machinefile is None:
        run_command = ['mpirun', '-n', num_processes, exec_path,
                       data_dir + '/' + param_file_name]
    else:
        os.environ['I_MPI_FABRICS_LIST'] = 'ofa'
        os.environ['OMP_NUM_THREADS'] = '1'
        run_command = ['mpirun', '-n', num_processes, '-f', data_dir + '/' +
                       machinefile, exec_path,
                       data_dir + '/' + param_file_name]

    if change_seed:
        random_seed = random.randint(0, 999999)
        params['BASE_SEED'] = random_seed

    if single_band is not None or single_comp is not None:
        currparams = read_parameter_file(data_dir + base_param_file)
        if single_band is not None:
            numband = int(currparams['NUMBAND'])
            for band in range(1, numband+1):
                if band != single_band:
                    params['INCLUDE_BAND{:03d}'.format(band)] = ".false."
                else:
                    params['INCLUDE_BAND{:03d}'.format(band)] = ".true."
        if single_comp is not None:
            numcomp = int(currparams['NUM_SIGNAL_COMPONENTS'])
            for comp in range(1, numcomp+1):
                if comp != single_comp:
                    params['INCLUDE_COMP{:02d}'.format(comp)] = ".false."
                else:
                    params['INCLUDE_COMP{:02d}'.format(comp)] = ".true."

    if base_param_file is not None:
        # Strictly, most of the above is redundant if it is None..
        params.update(param_dict)
        process_parameter_file(
            data_dir + base_param_file, data_dir + param_file_name,
            new_parameter_dict=params)

        shutil.copyfile(data_dir + param_file_name, chain_dir + param_file_name)
    currdir = os.getcwd()

    os.chdir(data_dir)
    with open(slurm_name, 'w') as slurm_file:
        with open(errlog_name, 'w') as error_file:
            process = subprocess.Popen(
                run_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            for stdout_line in process.stdout:
                print(stdout_line.decode(), end='')
                slurm_file.write(stdout_line.decode())
                slurm_file.flush()
            for errline in process.stderr:
                error_file.write(errline.decode())
                error_file.flush()
            del process

    os.chdir(currdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run Commander more easily.")
    parser.add_argument(
        'data_dir',
        type=str,
        help='The directory (starting from the base data directory) where the parameter file can be found, and inside which the chain directory will be created.')
    parser.add_argument(
        'run_name', 
        type=str, 
        help='The name of this run. Will be used in the name of the parameter file, as well as the name of the chain directory.')
    parser.add_argument(
        'num_processes',
        type=str,
        help='The number of MPI processes with which to run Commander.'
    )
    parser.add_argument(
        '--build',
        type=str,
        help='The name of the build (using Maksym\'s cmake structure). If --commander1 is set then this is not needed. Otherwise it is',
        default=None
    )
    parser.add_argument(
        '--no-seed-change',
        dest='no_seed_change',
        action='store_true',
        help="Don't change the seed for this run."
    )
    parser.add_argument(
        '--commander1',
        dest='commander1',
        action='store_true',
        help='Run Commander 1, not Commander 2 (or 3)'
    )
    parser.add_argument(
        '--set_parameters', dest='param_dict', action=StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...", default={}
    )
    parser.add_argument(
        '--delete-existing-dir',
        dest='delete_existing_dir',
        action='store_true',
        help="If the chain directory already exists, delete it and its contents. (If this is not set, an error will be thrown instead)"
    )
    parser.add_argument(
        '-machinefile',
        dest='machinefile',
        type=str,
        help="The machine file to use (for Commander 2/3)"
    )
    parser.add_argument(
        '--base_param_file',
        dest='base_param_file',
        type=str,
        help='The parameter file based on which the final parameter file will be created (relative to data_dir). If empty, will look for the parameter file named after the run that is specified, and no parameters can be modified.',
        default=None
    )
    parser.add_argument(
        '--single_band',
        dest='single_band',
        type=int,
        help="Whether to only run a single band, and which (accepted values are 1, 2, 3, ... corresponding to which band.)"
    )
    parser.add_argument(
        '--single_comp',
        dest='single_comp',
        type=int,
        help="Whether to only run a single component, and which (accepted values are 1, 2, 3, ... corresponding to which component.)"
    )


#    print(read_parameter_file('/mn/stornext/u3/eirikgje/data/cassiopeia/param_BP7.3.txt'))
#    read_parameter_file('/mn/stornext/u3/eirikgje/data/cassiopeia/param_BP7.3.txt')

    args = parser.parse_args()
    change_seed = False if args.no_seed_change else True
    delete_existing_dir = True if args.delete_existing_dir else False
    commander1 = True if args.commander1 else False
    if not commander1:
        if args.build is None:
            raise ValueError("Build must be specified when not using Commander1")
    machinefile = args.machinefile
    run_commander(args.data_dir, args.run_name,
                  args.num_processes, build=args.build, param_dict=args.param_dict,
                  change_seed=change_seed,
                  delete_existing_dir=delete_existing_dir,
                  commander1=commander1, machinefile=machinefile,
                  base_param_file=args.base_param_file, single_band=args.single_band,
                  single_comp=args.single_comp)
