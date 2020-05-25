#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge
# Valmor F. de Almeida dealmeidavf@gmail.com
'''
US COVID-19 surge period analysis.

Expand on this later.
'''

import numpy as np

from covid_surge import Surge

def test_main():

    # Get all US surge data including states.
    us_surge = Surge()

    # Set parameters
    us_surge.end_date = '5/15/20'       # set end date wanted
    us_surge.ignore_last_n_days = 0 # allow for data repo to be corrected/updated

    #****************************************************************************
    # Combine all states into a country
    #****************************************************************************
    print('********************************************************************')
    print('*                             US                                   *')
    print('********************************************************************')

    print('# of states/distric: ',len(us_surge.names))
    print('# of days:           ',us_surge.dates.shape[0])

    # Plot the data
    us_surge.plot_covid_data( save=True )

    print('')

    # Fit data to model function
    param_vec = us_surge.fit_data()

    #print(list(param_vec))
    param_gold = np.array([97537.82769142388,24.4213468857896,
                          -0.09760783162924842])
    assert np.allclose(param_vec,param_gold)
    print('')

    # Plot the fit data to model function of combined US data
    us_surge.plot_covid_nlfit( param_vec, save=True,
            plot_prime=True, plot_double_prime=True )

    # Report critical times
    (tc,dtc) = us_surge.critical_times( param_vec, verbose=True )

    #print(tc,dtc)
    tc_gold  = 32.737717546347874
    dtc_gold = 13.492338421440632
    assert np.allclose( np.array([tc,dtc]), np.array([tc_gold,dtc_gold]) )

    # Report errors 
    us_surge.error_analysis( param_vec, tc, dtc )

if __name__ == '__main__':
    test_main()
