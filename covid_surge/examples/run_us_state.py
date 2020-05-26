#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge
# Valmor F. de Almeida dealmeidavf@gmail.com
'''
US COVID-19 surge period analysis.

Expand on this later.
'''

from covid_surge import Surge

def main():

    # Get US surge data
    us_surge = Surge()

    # Set parameters
    us_surge.end_date = '4/20/20'       # set end date wanted
    us_surge.end_date = None            # get all the data available
    us_surge.ignore_last_n_days = 2 # allow for data repo to be corrected/updated

    #****************************************************************************
    # Single State Case
    #****************************************************************************
    print('********************************************************************')
    print('*                        Single State                              *')
    print('********************************************************************')

    name = 'North Carolina'
    print(name)
    print('')

    # Plot the data
    us_surge.plot_covid_data( name, save=True )

    n_last_days = 7
    state_id = us_surge.names.index(name)
    print('')
    print('Last %i days'%n_last_days,
          ' # of cumulative cases = ', us_surge.cases[-n_last_days:,state_id])
    print('Last %i days'%n_last_days,
          ' # of added cases =',
          [b-a for (b,a) in zip( us_surge.cases[-(n_last_days-1):,state_id],
                                 us_surge.cases[-n_last_days:-1,state_id] )
        ])
    print('')

    # Fit data to model function
    param_vec = us_surge.fit_data( name )
    print('')

    # Plot the fit data to model function
    us_surge.plot_covid_nlfit(param_vec, name, save=True,
            plot_prime=True, plot_double_prime=True)

    # Report critical times
    (tc,dtc) = us_surge.critical_times( param_vec, name, verbose=True )

    # Report errors
    us_surge.error_analysis( param_vec, tc, dtc, name )

    # 60-day look-ahead
    n_prediction_days = 60

    last_day = us_surge.dates.size
    total_deaths_predicted = int( us_surge.sigmoid_func(n_prediction_days + last_day, param_vec) )

    print('')
    print('Estimated cumulative deaths in %s days from %s = %6i'%(n_prediction_days,us_surge.dates[-1],total_deaths_predicted))
    print('# of cumulative deaths today, %s               = %6i'%(us_surge.dates[-1],us_surge.cases[-1,us_surge.names.index(name)]))
    print('')

if __name__ == '__main__':
    main()
