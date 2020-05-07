#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the COVID-surge application.
# https://github/dpploy/covid-surge

import os
import logging
import time
import datetime

class Surge:

    def __init__(self, locale='US', log_filename='covid_surge'):

        ( state_names, population, dates, cases ) = self.__get_covid_19_us_data()

        self.state_names = state_names
        self.population = population
        self.dates = dates
        self.cases = cases

        return

    def __get_covid_19_us_data(self, type='deaths' ):
        '''
        Load COVID-19 pandemic cumulative data from:

         https://github.com/CSSEGISandData/COVID-19.

        Parameters
        ----------
        type:  str, optional
                Type of data. Deaths ('deaths') and confirmed cases ('confirmed').
                Default: 'deaths'.

        Returns
        -------
        data: tuple(int, list(str), list(int))
               (population, dates, cases)

        '''

        import pandas as pd

        if type == 'deaths':

            df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
            #df.to_html('covid_19_deaths.html')

        elif type == 'confirmed':

            df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
            df_pop = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
            #df.to_html('covid_19_deaths.html')
            #df.to_html('covid_19_confirmed.html')

        else:
            assert True, 'invalid query type: %r (valid: "deaths", "confirmed"'%(type)

        df = df.drop(['UID','iso2','iso3','Combined_Key','code3','FIPS','Lat', 'Long_','Country_Region'],axis=1)

        df = df.rename(columns={'Province_State':'state/province','Admin2':'city'})

        import numpy as np

        state_names = list()

        state_names_tmp = list()

        for (i,istate) in enumerate(df['state/province']):
            if istate.strip() == 'Wyoming' and df.loc[i,'city']=='Weston':
                break
            state_names_tmp.append(istate)

        state_names_set = set(state_names_tmp)

        state_names = list(state_names_set)
        state_names = sorted(state_names)

        dates = np.array(list(df.columns[3:]))

        population = [0]*len(state_names)
        cases = np.zeros( (len(df.columns[3:]),len(state_names)), dtype=np.float64)

        for (i,istate) in enumerate(df['state/province']):
            if istate.strip() == 'Wyoming' and df.loc[i,'city']=='Weston':
                break

            state_id = state_names.index(istate)
            if type == 'confirmed':
                population[state_id] += int(df_pop.loc[i,'Population'])
            else:
                population[state_id] += int(df.loc[i,'Population'])

            cases[:,state_id] += np.array(list(df.loc[i, df.columns[3:]]))

        return ( state_names, population, dates, cases )
