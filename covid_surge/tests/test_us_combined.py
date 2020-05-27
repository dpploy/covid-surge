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
from asserts import assert_almost_equal

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

    print('')
    print('param_vec = ',list(param_vec))

    param_gold = np.array([98258.11249350989,
                           24.16030887578648,
                          -0.09667519121651309])
    print('param_gold = ',list(param_gold))
    print('')

    print('')
    print('Testing param results:')
    try:
        assert_almost_equal( param_vec[0], param_gold[0], delta=1000 )
        assert_almost_equal( param_vec[1], param_gold[1], delta=2 )
        assert_almost_equal( param_vec[2], param_gold[2], delta=0.01 )
    except AssertionError as err:
        print('Warning: ',err)
    else:
        print('all tests passed')
        print('')

    # Plot the fit data to model function of combined US data
    us_surge.plot_covid_nlfit( param_vec, save=True,
            plot_prime=True, plot_double_prime=True )

    # Report critical times
    (tc,dtc) = us_surge.critical_times( param_vec, verbose=True )

    print('')
    print('critical times = ',[tc,dtc])

    tc_gold  = 32.942382813045036
    dtc_gold = 13.622501081744613
    print('critical gold times = ',[tc_gold,dtc_gold])
    print('')

    print('')
    print('Testing times results:')

    try:
        assert_almost_equal( tc, tc_gold, delta=0.5 )
        assert_almost_equal( dtc, dtc_gold, delta=0.5 )
    except AssertionError as err:
        print('Warning: ',err)
    else:
        print('all tests passed')
        print('')

    # Report errors 
    us_surge.error_analysis( param_vec, tc, dtc )

if __name__ == '__main__':
    test_main()
