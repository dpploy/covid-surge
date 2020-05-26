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

def main():

    # Get all US surge data including states.
    us_surge = Surge()

    # Set parameters
    us_surge.end_date = '4/20/20'       # set end date wanted
    us_surge.end_date = None            # get all the data available
    us_surge.ignore_last_n_days = 2 # allow for data repo to be corrected/updated

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

    n_last_days = 7
    print('')
    print('Last %i days'%n_last_days, ' # of cumulative cases = ',
          np.sum(us_surge.cases,axis=1)[-n_last_days:])
    print('Last %i days'%n_last_days, ' # of added cases =',
          [b-a for (b,a) in zip( np.sum(us_surge.cases,axis=1)[-(n_last_days-1):],
                               np.sum(us_surge.cases,axis=1)[-n_last_days:-1] )
        ])
    print('')

    # Fit data to model function
    param_vec = us_surge.fit_data()
    print('')

    # Plot the fit data to model function of combined US data
    us_surge.plot_covid_nlfit( param_vec, save=True,
            plot_prime=True, plot_double_prime=True )

    # Report critical times
    (tc,dtc) = us_surge.critical_times( param_vec, verbose=True )

    # Report errors
    us_surge.error_analysis( param_vec, tc, dtc )

    # 60-day look-ahead
    n_prediction_days = 60

    last_day = us_surge.dates.size
    total_deaths_predicted = int( us_surge.sigmoid_func(n_prediction_days + last_day, param_vec) )

    print('')
    print('Estimated cumulative deaths in %s days from %s = %6i'%(n_prediction_days,us_surge.dates[-1],total_deaths_predicted))
    print('# of cumulative deaths today, %s               = %6i'%(us_surge.dates[-1],np.sum(us_surge.cases[-1,:])))
    print('')

if __name__ == '__main__':
    main()
