import healpy
import matplotlib.pyplot as plt
import numpy as np
import argparse

def plot_things(data_directory, pixel_number, signal_type, sample_range,
                plot_prefix):
    signal_map = {'I': 0,
                  'Q': 1,
                  'U': 2}
    component_points = {}
    fig, axes = plt.subplots(8, 1, sharex=True)
#    plt.figure(1)
    for i, (component, component_desc) in enumerate(zip(
            ['chisq', 'cmb', 'cmb_Cl', 'dust_beta', 'dust', 'dust_Td',
             'synch_beta', 'synch'], 
            ['Chi-squared', 'Sigma', 'Cl', 'Beta_d', 'amp_d', 'T_d', 'Beta_s',
             'amp_s'])):
        datapoints = []
        for sample in range(sample_range[0], sample_range[1]):
            curr_sample = healpy.read_map(data_directory + component + '_c0001_k{:0>5}.fits'.format(sample), field=signal_map[signal_type])
            datapoints.append(curr_sample[pixel_number])
        datapoints = np.array(datapoints)
        component_points[component] = datapoints
        axes[i].plot(component_points[component], label=component_desc)
        axes[i].legend()
    fig.subplots_adjust(hspace=0)
    fig.savefig(plot_prefix + 'pixplot.png')
    return component_points


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Make traceplots of Commander output")
    parser.add_argument(
        'directory',
        type=str,
        help='The directory containing the chains'
    )
    parser.add_argument(
        'pixel_number',
        type=int,
        help='The pixel number to plot.'
    )
    parser.add_argument(
        'signal_type',
        type=str,
        choices=['I', 'Q', 'U']
    )
    parser.add_argument(
        'start_sample',
        type=int
    )
    parser.add_argument(
        'end_sample',
        type=int
    )
    parser.add_argument(
        'plot_prefix',
        type=str
    )
    args = parser.parse_args()
    plot_things(args.directory, args.pixel_number, args.signal_type,
                [args.start_sample, args.end_sample+1], args.plot_prefix)
