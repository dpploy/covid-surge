#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the covid-surge application.
# https://github/dpploy/covid-surge
def color_map( num_colors ):
    '''
    Nice colormap for plotting.

    Parameters
    ----------
    num_colors: int, required
        Number of colors.

    Returns
    -------
    color_map: list(tuple(R,G,B,A))
        List with colors interpolated from internal list of primary colors.

    '''

    assert num_colors >= 1

    import numpy as np

    # primary colors
    # use the RGBA decimal code
    red     = np.array((1,0,0,1))
    blue    = np.array((0,0,1,1))
    magenta = np.array((1,0,1,1))
    green   = np.array((0,1,0,1))
    orange  = np.array((1,0.5,0,1))
    black   = np.array((0,0,0,1))
    yellow  = np.array((1,1,0,1))
    cyan    = np.array((0,1,1,1))

    # order the primary colors here
    color_map = list()
    color_map = [red, blue, orange, magenta, green, yellow, cyan, black]

    num_primary_colors = len(color_map)

    if num_colors <= num_primary_colors:
        return color_map[:num_colors]

    # interpolate primary colors
    while len(color_map) < num_colors:
        j = 0
        for i in range(len(color_map)-1):
            color_a = color_map[2*i]
            color_b = color_map[2*i+1]
            mid_color = (color_a+color_b)/2.0
            j = 2*i+1
            color_map.insert(j,mid_color) # insert before index
            if len(color_map) == num_colors:
                break

    return color_map
#*********************************************************************************
def get_covid_19_us_data( type='deaths' ):
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
#*********************************************************************************
def get_covid_19_global_data( type='deaths', distribution=True, cumulative=False ):
    '''
    Load COVID-19 pandemic cumulative data from:

        https://github.com/CSSEGISandData/COVID-19

    Parameters
    ----------
    type: str, optional
        Type of data. Deaths ('deaths') and confirmed cases ('confirmed').
        Default: 'deaths'.

    distribution: bool, optional
        Distribution of new cases over dates.
        Default: True

    cumulative: bool, optional
        Cumulative number of cases over dates.
        Default: False

    Returns
    -------
    data: tuple(int, list(str), list(int))
           (contry_names, dates, cases)

    '''

    if cumulative is True:
        distribution = False

    import pandas as pd

    if type == 'deaths':
        df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        #df.to_html('covid_19_global_deaths.html')

    else:
        assert True, 'invalid query type: %r (valid: "deaths"'%(type)

    df = df.drop(['Lat', 'Long'],axis=1)
    df = df.rename(columns={'Province/State':'state/province','Country/Region':'country/region'})

    import numpy as np

    country_names = list()

    country_names_tmp = list()

    for (i,icountry) in enumerate(df['country/region']):
        country_names_tmp.append(icountry)

    country_names_set = set(country_names_tmp)

    country_names = list(country_names_set)
    country_names = sorted(country_names)

    dates = np.array(list(df.columns[2:]))

    cases = np.zeros( (len(df.columns[2:]),len(country_names)), dtype=np.float64)

    for (i,icountry) in enumerate(df['country/region']):

        country_id = country_names.index(icountry)

        cases[:,country_id] += np.array(list(df.loc[i, df.columns[2:]]))

    if distribution:

        for j in range(cases.shape[1]):
            cases[:,j] = np.round(np.gradient( cases[:,j] ),0)

    return ( country_names, dates, cases )
#*********************************************************************************
