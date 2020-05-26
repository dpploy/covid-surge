#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge
# Valmor F. de Almeida dealmeidavf@gmail.com
'''
Global COVID-19 surge period analysis.

Expand on this later.
'''

from covid_surge import Surge

def main():

    # Get global surge data
    g_surge = Surge(locale='global')

    print('# of countries: ',g_surge.cases.shape[1])
    print('# of days:      ',g_surge.cases.shape[0])

    # Set parameters
    g_surge.end_date = '4/20/20'       # set end date wanted
    g_surge.end_date = None            # get all the data available
    g_surge.ignore_last_n_days = 2 # allow for data repo to be corrected/updated

    print('********************************************************************')
    print('*                        Single Country                            *')
    print('********************************************************************')

    name = 'US'
    print(name)
    print('')

    # Plot the data
    g_surge.plot_covid_data( name, save=True )

    n_last_days = 7
    country_id = g_surge.names.index(name)
    print('')
    print('Last %i days'%n_last_days,
          ' # of cumulative cases = ', g_surge.cases[-n_last_days:,country_id])
    print('Last %i days'%n_last_days,
          ' # of added cases =',
          [b-a for (b,a) in zip( g_surge.cases[-(n_last_days-1):,country_id],
                                 g_surge.cases[-n_last_days:-1,country_id] )
        ])
    print('')

    # Fit data to model function
    param_vec = g_surge.fit_data( name )
    print('')

    # Plot the fit data to model function
    g_surge.plot_covid_nlfit( param_vec, name, save=True,
            plot_prime=True, plot_double_prime=True )

    # Report critical times
    (tc,dtc) = g_surge.critical_times( param_vec, name, verbose=True )

    # Report errors
    g_surge.error_analysis( param_vec, tc, dtc, name )

    # 60-day look-ahead
    n_prediction_days = 60

    last_day = g_surge.dates.size
    total_deaths_predicted = int( g_surge.sigmoid_func(n_prediction_days + last_day, param_vec) )

    print('')
    print('Estimated cumulative deaths in %s days from %s = %6i'%(n_prediction_days,g_surge.dates[-1],total_deaths_predicted))
    print('# of cumulative deaths today, %s               = %6i'%(g_surge.dates[-1],g_surge.cases[-1,g_surge.names.index(name)]))
    print('')

if __name__ == '__main__':
    main()
