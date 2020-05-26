#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge
# Valmor F. de Almeida dealmeidavf@gmail.com
'''
US States COVID-19 surge period analysis.

Expand on this later.
'''

from covid_surge import Surge

def main():

    # Get US surge data
    us_surge = Surge()

    # Set parameters
    us_surge.end_date = '4/20/20'   # set end date wanted
    us_surge.end_date = None        # get all the data available
    us_surge.ignore_last_n_days = 2 # allow for data repo to be corrected/updated
    us_surge.min_n_cases_abs = 500  # min # of absolute cases for analysis
    us_surge.deaths_100k_minimum = 41 # US death per 100,000 for Chronic Lower Respiratory Diseases per year: 41 (2019)

    print('')
    print('# of states/distric: ',len(us_surge.names))
    print('# of days:           ',us_surge.dates.shape[0])

    # Fit data to all states
    fit_data = us_surge.multi_fit_data(verbose=True, plot=True, save_plots=True)

    # Plot all data in one plot
    us_surge.plot_multi_fit_data( fit_data, 'experimental', save=True )
    # Plot all fit data in one plot
    us_surge.plot_multi_fit_data( fit_data, 'fit', save=True )

    # Create clustering bins based on surge period
    bins = us_surge.clustering(fit_data,2,'surge_period')

    print('')
    print('*****************************************************************')
    print('                             Bins                                ')
    print('*****************************************************************')
    for k in sorted(bins.keys()):
        print(' Bin %i %s'%(k,bins[k]))

    # Use bins to create groups of states based on surge period
    state_groups = dict()

    for (sort_key,data) in fit_data:
        state = data[0]
        param_vec = data[3]
        key = us_surge.get_bin_id(sort_key,bins)
        if key in state_groups:
            state_groups[key].append(state)
        else:
            state_groups[key] = list()
            state_groups[key].append(state)

    state_groups = [ state_groups[k] for k in
                     sorted(state_groups.keys(),reverse=False) ]

    print('')
    print('*****************************************************************')
    print('                         Country Groups                          ')
    print('*****************************************************************')
    for g in state_groups:
        print(' Group %i %s'%(state_groups.index(g),g))

    # Plot the normalized surge for groups of states
    us_surge.plot_group_fit_data( state_groups, fit_data, save=True )

    # Plot the surge period for all grouped states
    us_surge.plot_group_surge_periods( fit_data, bins, save=True )

if __name__ == '__main__':
    main()
