import numpy as np
from scipy.optimize import fmin_powell

def fit_cossquared(data):
    x = np.arange(len(data))
    nonzerofilter = (data != 0) & (data < 0.15)
    def data_model(params, data=data, x=x, nonzerofilter=nonzerofilter):
        if (params[0] < 0.8 * (np.max(data[nonzerofilter]) - np.min(data[nonzerofilter]))):
            return 1e30
        if np.abs(params[1]) > 2*np.pi/10000.0 or np.abs(params[1]) < 2 * np.pi / 30000:
            return 1e30
        model = params[0] * np.cos(params[1] * x + params[2])**2 + params[3]
        return np.sum((data[nonzerofilter] - model[nonzerofilter]) ** 2)
    
    return fmin_powell(data_model, np.array([1.0, 2 * np.pi/10000.0, 0.0, 0.0]))
