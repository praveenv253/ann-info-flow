#!/usr/bin/env python3

from __future__ import print_function, division

import os
import sys
import joblib

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from param_utils import init_params
from pruning import edge_list
from nn import SimpleNet  # Required for joblib.load to work - weird bug
# https://stackoverflow.com/questions/49621169/joblib-load-main-attributeerror


def fit_line(x, y):
    """
    Fit a line without an intercept and compute the R^2 value.
    `x` and `y` should 1D arrays.
    """

    # Estimated slope using pseudo-inverse
    mhat = (x @ y) / np.sum(x**2)
    # R^2 value: fraction of explained variance
    r2val = 1 - np.sum((y - mhat * x)**2) / np.sum((y - y.mean())**2)

    return mhat, r2val


if __name__ == '__main__':
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
    else:
        params = init_params()
        dataset = params.dataset

    if len(sys.argv) > 2:
        subfolder = sys.argv[2]
    else:
        subfolder = ''

    #subfolder = 'linear-svm'
    results_dir = 'results-%s' % dataset
    results_subfolder = os.path.join(results_dir, subfolder)

    data = np.load(results_subfolder + '/scaling.npz')
    num_runs = data['acc_flows'].shape[0]
    acc_flows = data['acc_flows'].flatten() * 100       # Convert to percentages
    delta_accs = data['delta_accs'].flatten() * 100
    bias_flows = data['bias_flows'].flatten() * 100
    delta_biases = data['delta_biases'].flatten() * 100

    # Also load the analysis file to extract unweighted flows
    rets_before = joblib.load(results_subfolder + '/analyzed-data.pkl')
    y_info_flows = [ret[4] for ret in rets_before]
    z_info_flows = [ret[1] for ret in rets_before]

    trained_nets = joblib.load(results_dir + '/trained-nets.pkl')
    layers = [np.array(edge_list(net))[:, 0] for net in trained_nets]
    weights = [edge_list(net, net.get_weights())[1] for net in trained_nets]
    layers = np.array(layers).flatten()
    weights = np.array(weights).flatten()

    title_kwargs = dict(fontsize=18)
    label_kwargs = dict(fontsize=16)
    ticksize = 14

    #colors = [cm.tab20c(i) for i in [0, 2, 4, 6, 8, 10]]
    colors = np.array([cm.Paired(i) for i in [0, 1, 8, 9, 6, 7, 4, 5]])
    line_kwargs = dict(marker='o', markersize=5, linestyle='none', mew=0)

    info_method = 'Correlation'
    if subfolder == 'linear-svm':
        info_method = 'Linear SVM'
    elif subfolder == 'kernel-svm':
        info_method = 'Kernel SVM'

    if 'adult' in dataset:
        dataset = 'Adult'
    elif dataset == 'tinyscm':
        dataset = 'Synthetic'

    # Plot acc/bias change against absolute weighted information flows
    plt.figure()
    ax = plt.gca()
    acc_flow_meas = abs(acc_flows)
    #acc_flow_meas = acc_flows / weights.flatten()
    plt.plot(acc_flow_meas[layers == 0], delta_accs[layers == 0], color=colors[0], **line_kwargs)
    plt.plot(acc_flow_meas[layers == 1], delta_accs[layers == 1], color=colors[1], **line_kwargs)
    # Compute regression lines for delta_acc & delta_bias vs. resp flow
    slope, intercept, rval0 = stats.linregress(acc_flow_meas[layers == 0], delta_accs[layers == 0])[:3]
    x = np.r_[min(acc_flow_meas), 0.5 * max(acc_flow_meas)]
    plt.plot(x, slope * x + intercept, color='darkgrey')
    slope, intercept, rval1 = stats.linregress(acc_flow_meas[layers == 1], delta_accs[layers == 1])[:3]
    x = np.r_[min(acc_flow_meas), max(acc_flow_meas)]
    plt.plot(x, slope * x + intercept, color='k')
    #slope, r2val = fit_line(abs(acc_flows), delta_accs)
    #x = np.r_[min(abs(acc_flows)), max(abs(acc_flows))]
    #plt.plot(x, slope * x, 'k-')
    #print(r2val)
    plt.title('$\Delta_{acc}$ vs. weighted acc flow\n(Dataset: %s, MI est: %s)' % (dataset, info_method), **title_kwargs)
    plt.xlabel(r'Weighted accuracy flow, $\mathcal{F}_Y(E_t)$', **label_kwargs)
    plt.ylabel('Change in output acc upon pruning\n(new acc - old acc, %-points)', **label_kwargs)
    plt.gca().tick_params(axis='both', which='major', labelsize=ticksize)
    plt.text(0.05, 0.05, '$R^2_1 = %.2f$\n$R^2_2 = %.2f$' % (rval0**2, rval1**2), fontsize=16,
             horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes)
    plt.tight_layout()

    plt.figure()
    ax = plt.gca()
    bias_flow_meas = abs(bias_flows)
    #bias_flow_meas = bias_flows / weights.flatten()
    #plt.plot(bias_flow_meas, delta_biases, 'C1o')
    plt.plot(bias_flow_meas[layers == 0], delta_biases[layers == 0], color=colors[4], **line_kwargs)
    plt.plot(bias_flow_meas[layers == 1], delta_biases[layers == 1], color=colors[5], **line_kwargs)
    # Compute regression lines for delta_acc & delta_bias vs. resp flow
    slope, intercept, rval0 = stats.linregress(bias_flow_meas[layers == 0], delta_biases[layers == 0])[:3]
    x = np.r_[min(bias_flow_meas), max(bias_flow_meas)]
    plt.plot(x, slope * x + intercept, color='darkgrey')
    slope, intercept, rval1 = stats.linregress(bias_flow_meas[layers == 1], delta_biases[layers == 1])[:3]
    x = np.r_[min(bias_flow_meas), max(bias_flow_meas)]
    plt.plot(x, slope * x + intercept, color='k')
    #slope, r2val = fit_line(abs(bias_flows), delta_biases)
    #x = np.r_[min(abs(bias_flows)), max(abs(bias_flows))]
    #plt.plot(x, slope * x, 'k-')
    #print(r2val)
    plt.title('$\Delta_{bias}$ vs. weighted bias flow\n(Dataset: %s, MI est: %s)' % (dataset, info_method), **title_kwargs)
    plt.xlabel(r'Weighted bias flow, $\mathcal{F}_Z(E_t)$', **label_kwargs)
    plt.ylabel('Change in output bias upon pruning\n(new bias - old bias; %-points)', **label_kwargs)
    plt.text(0.05, 0.05, '$R^2_1 = %.2f$\n$R^2_2 = %.2f$' % (rval0**2, rval1**2), fontsize=16,
             horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes)
    plt.gca().tick_params(axis='both', which='major', labelsize=ticksize)
    plt.tight_layout()

    ## Plot acc/bias change against signed weighted information flow measures
    #plt.figure()
    #plt.plot(acc_flows, delta_accs, 'C0o')
    #plt.title('$\Delta_{acc}$ vs signed weighted acc flow\n(%s dataset)' % dataset, **title_kwargs)
    #plt.xlabel('Signed weighted accuracy flow', **label_kwargs)
    #plt.ylabel('Change in output acc upon pruning\n(new acc - old acc)', **label_kwargs)
    #plt.tight_layout()

    #plt.figure()
    #plt.plot(bias_flows, delta_biases, 'C1o')
    #plt.title('$\Delta_{bias}$ vs signed weighted bias flow\n(%s dataset)' % dataset, **title_kwargs)
    #plt.xlabel('Signed weighted bias flow', **label_kwargs)
    #plt.ylabel('Change in output bias upon pruning\n(new bias - old bias)', **label_kwargs)
    #plt.tight_layout()

    ## Plot acc/bias change against acc/bias ratio
    #plt.figure()
    #acc_flow_meas = np.log10(abs(acc_flows) / abs(bias_flows) / abs(weights))
    ##plt.plot(abs(acc_flows) - abs(bias_flows), delta_accs, 'C0o')
    #plt.plot(acc_flow_meas[layers == 0], delta_accs[layers == 0], 'C0o', alpha=0.3)
    #plt.plot(acc_flow_meas[layers == 1], delta_accs[layers == 1], 'C0o')
    #plt.title('$\Delta_{acc}$ vs acc/bias flow ratio\n(%s dataset)' % dataset, **title_kwargs)
    #plt.xlabel('log_10(Acc / (|Weight| * bias flow))', **label_kwargs)
    #plt.ylabel('Change in output acc upon pruning\n(new acc - old acc)', **label_kwargs)
    #plt.tight_layout()

    ## Plot acc/bias change against bias/acc ratio
    #plt.figure()
    #bias_flow_meas = np.log10(abs(weights) * abs(bias_flows) / abs(acc_flows))
    ##plt.plot(abs(bias_flows) - abs(acc_flows), delta_biases, 'C1o')
    #plt.plot(bias_flow_meas[layers == 0], delta_biases[layers == 0], 'C1o', alpha=0.3)
    #plt.plot(bias_flow_meas[layers == 1], delta_biases[layers == 1], 'C1o')
    #plt.title('$\Delta_{bias}$ vs bias/acc flow ratio\n(%s dataset)' % dataset, **title_kwargs)
    #plt.xlabel('log_10(|Weight| * Bias / Acc flow)', **label_kwargs)
    #plt.ylabel('Change in output bias upon pruning\n(new bias - old bias)', **label_kwargs)
    #plt.tight_layout()

    # TODO: Plot weighted acc/bias flow ratios - to do this, it would be easier
    # to just load from the analyzed-data file directly.

    ## Plot edge-wise accuracies and biases in a 2D scatter plot; color by run
    #plt.figure()
    ##inds = (data['bias_flows'] > 0) & (data['acc_flows'] > 0)
    ##plt.plot(data['bias_flows'][inds].squeeze(), data['acc_flows'][inds].squeeze(), 'o')
    #plt.plot((data['bias_flows'].squeeze() / weights).T, (data['acc_flows'].squeeze() / weights).T, 'o')
    #plt.title('Accuracy and Bias flows for every edge', **title_kwargs)
    #plt.xlabel('Bias', **label_kwargs)
    #plt.ylabel('Accuracy', **label_kwargs)
    #plt.tight_layout()

    plt.show()
