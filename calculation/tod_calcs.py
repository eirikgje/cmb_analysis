import numpy as np
import math

def bin_phases(tod, sample_frequency, bin_width, target_period):
    num_bins = math.ceil(target_period / bin_width)
    binned_data = np.zeros(num_bins)
    currlim = sample_frequency * bin_width
    currbin = 0
    for i, el in enumerate(tod):
        if i > currlim:
            currlim += sample_frequency * bin_width
            currbin += 1
            currbin = currbin % num_bins
        binned_data[currbin] += el
    return binned_data


def downsample_tod(tod, orig_frequency, target_frequency):
    samples_per_sample = orig_frequency / target_frequency

    j = 0
    curr_count = 0
    downsampled_tod = []
    curr_bin = 0

    for i, el in enumerate(tod):
        if i > (j+1) * samples_per_sample:
            curr_bin /= curr_count
            downsampled_tod.append(curr_bin)
            j += 1
            curr_bin = 0
            curr_count = 0
        curr_bin += el
        curr_count += 1
    return downsampled_tod



