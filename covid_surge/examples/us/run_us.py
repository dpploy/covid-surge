#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge
'''
US COVID-19 surge period analysis.

Expand on this later.
'''

import numpy as np

from covid_surge import Surge

def main():

    # Get US surge data
    us_surge = Surge()

    print('# of states/distric: ',len(us_surge.state_names))
    print('# of days:           ',us_surge.dates.shape[0])

    # Set oldest value for date and 
    us_surge.end_date = '4/20/20'       # set end date wanted
    us_surge.end_date = None            # get all the data available
    us_surge.ignore_last_n_days = 2 # allow for data repo to be corrected/updated

    # Plot the data
    us_surge.plot_covid_data( 'combined' )

    print('')
    print('Last 5 days # of cumulative cases =',np.sum(us_surge.cases,axis=1)[-5:])
    print('Last 5 days # of added cases =',
        [b-a for (b,a) in zip( np.sum(us_surge.cases,axis=1)[-4:],
                               np.sum(us_surge.cases,axis=1)[-5:-1] )
        ]
         )
    print('')

    # Fit data to model function
    param_vec = us_surge.fit_data( 'combined' )
    print('')

    # Plot the fit data to model function
    us_surge.plot_covid_nlfit('combined', param_vec )

    # Report critical times
    (tc,dtc) = us_surge.critical_times( 'combined', param_vec )

    # Report errors 
    us_surge.error_analysis( 'combined', param_vec, tc, dtc )

if __name__ == '__main__':
    main()
