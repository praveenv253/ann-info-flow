import numpy as np
from types import SimpleNamespace
import torch.nn as nn


# Initialize parameters
def init_params(params=None, dataset=None):
    # TODO: Make this into a class. The initialization is safer to do that way

    # Create a new namespace only if one has not already been provided
    if params is None:
        params = SimpleNamespace()

    # Data parameters
    params.datasets = ['tinyscm', 'adult-small', 'adult-large']
    if dataset is None:
        params.dataset = params.datasets[0]
    elif dataset in params.datasets:
        params.dataset = dataset
    else:
        raise ValueError('Unrecognized dataset %s' % dataset)

    # Parameters specific to tinyscm
    params.num_data = 10000  # Should be moved to data.num_data etc at some point
    params.num_train = 5000
    params.datafile = 'results-%s/data-%d.pkl' % (params.dataset, params.num_data)
    params.force_regenerate = False # For simulated dataset
    #params.force_regenerate = True # For simulated dataset

    # ANN parameters
    params.annfile = 'results-%s/trained-nets.pkl' % params.dataset
    params.force_retrain = False

    # ANN training parameters for each dataset
    params.num_epochs = {'tinyscm': 50, 'adult-small': 50, 'adult-large': 50}
    params.minibatch_size = {'tinyscm': 10, 'adult-small': 10, 'adult-large': 10}  # Should be a factor of num_train for each dataset
    params.learning_rate = {'tinyscm': 0.03, 'adult-small': 3e-3, 'adult-large': 3e-3}
    params.momentum = {'tinyscm': 0.9, 'adult-small': 0.9, 'adult-large': 0.9}
    params.print_every_factor = {'tinyscm': 5, 'adult-small': 5, 'adult-large': 5}  # Prints more for larger numbers
    params.criterion = {
        #'tinyscm': nn.MSELoss(),
        'tinyscm': nn.CrossEntropyLoss(),  # expects 1-hot encoding at output of NN
        #'adult': nn.MSELoss(),
        'adult-small': nn.CrossEntropyLoss(),  # expects 1-hot encoding at output of NN
        'adult-large': nn.CrossEntropyLoss(),  # expects 1-hot encoding at output of NN
    }

    # Parameters for initial analysis of the ANN
    params.analysis_file = 'results-%s/analyzed-data.pkl' % params.dataset
    params.force_reanalyze = False
    params.info_methods = ['kernel-svm', 'linear-svm', 'corr']
    params.info_method = params.info_methods[0]

    # Parameters for pruning
    params.prune_metrics = ['biasacc', 'accbias', 'random']
    params.prune_methods = ['node', 'edge', 'path']
    params.prune_metric = params.prune_metrics[0]
    params.prune_method = params.prune_methods[1]
    params.num_to_prune = 2  # Number of nodes or edges to prune
    params.prune_factors = np.linspace(0, 1, 10, endpoint=False)
    #params.prune_factors = [0, 0.1, 0.5]
    params.num_runs = 1  # Number of times to run the analysis

    return params
