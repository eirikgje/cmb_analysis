import subprocess

def run_external_process(process_path,
                         argument_list,
                         is_mpi=False,
                         num_processes=None,
                         stdout_file='stdout.log',
                         stderr_file='stderr.log'):

    with open(stdout_file, 'w') as stdout_file:
        with open(stderr_file, 'w') as stderr_file:
            command = [process_path]
            command += argument_list
            if is_mpi:
                commmand = ['mpirun', '-n', str(num_processes)] + command
            process = subprocess.Popen(command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

            for stdout_line in process.stdout:
                print(stdout_line.decode(), end='')
                stdout_file.write(stdout_line.decode())
                stdout_file.flush()
            for errline in process.stderr:
                stderr_file.write(errline.decode())
                stderr_file.flush()
            del process
