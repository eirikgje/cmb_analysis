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

class StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        param_dict = {}
        for kv in values.split(","):
            k, v = kv.split("=")
            param_dict[k] = v
        setattr(namespace, self.dest, param_dict)

def run_commander(data_dir, run_name, base_param_file, num_processes,
                  param_dict={},
                  base_data_dir='/mn/stornext/u3/eirikgje/data/',
                  change_seed=True,
                  delete_existing_dir=False,
                  commander1=True,
                  machinefile=''):
    data_dir = base_data_dir + data_dir + '/'
    chain_dir = data_dir + 'chains_' + run_name + '/'
    if delete_existing_dir and os.path.isdir(chain_dir):
        shutil.rmtree(chain_dir)
    os.mkdir(chain_dir)
    if commander1:
        exec_path = '/mn/stornext/u3/eirikgje/src/Commander/commander1/src/commander/commander'
        params = {'CHAIN_DIRECTORY': '\'' + chain_dir + '\''}
    else:
        exec_path = '/mn/stornext/u3/eirikgje/src/Commander/src/commander/commander'
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
        'base_param_file',
        type=str,
        help='The parameter file based on which the final parameter file will be created (relative to data_dir).')
    parser.add_argument(
        'num_processes',
        type=str,
        help='The number of MPI processes with which to run Commander.'
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


    args = parser.parse_args()
    change_seed = False if args.no_seed_change else True
    delete_existing_dir = True if args.delete_existing_dir else False
    commander1 = True if args.commander1 else False
    machinefile = args.machinefile
    run_commander(args.data_dir, args.run_name, args.base_param_file,
                  args.num_processes, param_dict=args.param_dict,
                  change_seed=change_seed,
                  delete_existing_dir=delete_existing_dir,
                  commander1=commander1, machinefile=machinefile)
