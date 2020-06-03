import numpy as np

def moving_average(data, window_size, weights=None):
    # Pads symmetrically around start and end points

    padded_data = pad_data(data, window_size)
    if weights is not None:
        padded_weights = pad_data(weights, window_size)
    else:
        padded_weights = np.ones(len(padded_data))

    means = []
    for i in range(len(data)):
        means.append(np.average(padded_data[i:i+int(window_size)+1],
                                weights=padded_weights[i:i+int(window_size)+1]))

    return np.array(means)

def moving_variance(data, window_size):

    padded_data = np.append(np.append(data[int(window_size/2)-1::-1], data), data[-1:-int(window_size/2)-1:-1])

    variance = []

    for i in range(len(data)):
        variance.append(np.var(padded_data[i:i+int(window_size)+1]))

    return variance



def pad_data(data, window_size):
    padded_data = np.append(np.append(data[int(window_size/2)-1::-1], data), data[-1:-int(window_size/2)-1:-1])

    return padded_data
