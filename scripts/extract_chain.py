import h5py
import argparse

def extract(filename, iteration, outfilename):
    f = h5py.File(filename)
    iteration = '{:06d}'.format(iteration)
    outfile = h5py.File(outfilename, 'w')
    f.copy(iteration + '/ame', outfile['/'])
    f.copy(iteration + '/bandpass', outfile['/'])
    f.copy(iteration + '/cmb', outfile['/'])
    f.copy(iteration + '/dust', outfile['/'])
    f.copy(iteration + '/ff', outfile['/'])
    f.copy(iteration + '/gain', outfile['/'])
    f.copy(iteration + '/md', outfile['/'])
    f.copy(iteration + '/synch', outfile['/'])
    f.copy(iteration + '/tod', outfile['/'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract an iteration from a Commander 3 chain file")

    parser.add_argument(
        'chain_dir',
        type=str,
        help="The directory in which the chain file can be found"
    )

    parser.add_argument(
        'chain_file',
        type=str,
        help='The name of the chain file from which we want to extract'
    )
    parser.add_argument(
        'iteration',
        type=int,
        help='The iteration that we want to extract'
    )
    parser.add_argument(
        'outdir',
        type=str,
        help='The directory into which we want to put the extracted h5 file'
    )

    parser.add_argument(
        'out_file',
        type=str,
        help='The name of the output file (must be .h5)'
    )

    args = parser.parse_args()
    extract(args.chain_dir + '/' + args.chain_file,
            args.iteration,
            args.outdir + '/' + args.out_file)
