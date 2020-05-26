#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge
# Valmor F. de Almeida dealmeidavf@gmail.com
'''
Global COVID-19 surge period analysis.

Expand on this later.
'''

import numpy as np

from covid_surge import Surge

def test_main():

    # Get US surge data
    g_surge = Surge('global')

    # Set parameters
    g_surge.end_date = '5/15/20'   # set end date wanted
    g_surge.ignore_last_n_days = 0 # allow for data repo to be corrected/updated
    g_surge.min_n_cases_abs = 2500  # min # of absolute cases for analysis

    print('# of countries: ',g_surge.cases.shape[1])
    print('# of days:      ',g_surge.cases.shape[0])

    # Fit data to all states
    fit_data = g_surge.multi_fit_data(blocked_list=['China'],
            verbose=True, plot=True, save_plots=True)

    # Plot all data in one plot
    g_surge.plot_multi_fit_data( fit_data, 'experimental', save=True )
    # Plot all fit data in one plot
    g_surge.plot_multi_fit_data( fit_data, 'fit', save=True )

    # Create clustering bins based on surge period
    bins = g_surge.clustering(fit_data,2,'surge_period')

    print('')
    print('*****************************************************************')
    print('                             Bins                                ')
    print('*****************************************************************')
    for k in sorted(bins.keys()):
        print(' Bin %i %s'%(k,bins[k]))

    # Use bins to create groups of countries based on surge period
    country_groups = dict()

    for (sort_key,data) in fit_data:
        country = data[0]
        param_vec = data[3]
        key = g_surge.get_bin_id(sort_key,bins)
        if key in country_groups:
            country_groups[key].append(country)
        else:
            country_groups[key] = list()
            country_groups[key].append(country)

    country_groups = [ country_groups[k] for k in
                     sorted(country_groups.keys(),reverse=False) ]

    print('')
    print('*****************************************************************')
    print('                         Country Groups                          ')
    print('*****************************************************************')
    for g in country_groups:
        print(' Group %i %s'%(country_groups.index(g),g))

    assert len(country_groups) == 6
    assert country_groups[0] == ['Belgium', 'France']
    assert country_groups[1] == ['Germany', 'Turkey']
    assert country_groups[2] == ['Spain', 'Netherlands', 'United Kingdom', 'Canada']
    assert country_groups[3] == ['Ecuador', 'Sweden']
    assert country_groups[4] == ['US', 'Italy']
    assert country_groups[5] == ['Iran']

    # Plot the normalized surge for groups of countries
    g_surge.plot_group_fit_data( country_groups, fit_data, save=True )

    # Plot the surge period for all grouped states
    g_surge.plot_group_surge_periods( fit_data, bins, save=True )

if __name__ == '__main__':
    test_main()
