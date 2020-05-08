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

        self.__end_date           = None
        self.__ignore_last_n_days = 0

        ( state_names, populations, dates, cases ) = self.__get_covid_19_us_data()

        assert dates.size == cases.shape[0]
        assert len(state_names) == cases.shape[1]

        self.state_names = state_names
        self.populations = populations

        self.dates = dates
        self.cases = cases

        return

    def __set_end_date(self, v):

        assert isinstance(v,str) or v is None

        self.__end_date = v

        if self.__end_date is not None:
            assert isinstance(self.__end_date,str)
            (id,) = np.where(self.dates==self.__end_date)
            assert id.size == 1
            self.dates = np.copy(self.dates[:id[0]+1]))
            self.cases = np.copy(self.cases[:id[0]+1,:]))
        elif self.__ignore_last_n_days != 0:
            plot_dates = plot_dates[:-__ignore_last_n_days]
            plot_cases = plot_cases[:-__ignore_last_n_days]

        return

    def __get_end_date(self):

        return self.__end_date
    end_date = property(__get_end_date, __set_end_date, None, None)

    def __set_ignore_last_n_days(self, v):

        assert isinstance(v,int)
        assert v >= 0

        self.__ignore_last_n_days = v

        if self.__ignore_last_n_days != 0:

            plot_dates = plot_dates[:-__ignore_last_n_days]
            plot_cases = plot_cases[:-__ignore_last_n_days]

        return

    def __get_ignore_last_n_days(self):

        return self.__ignore_last_n_days
    ignore_last_n_days = property(__get_ignore_last_n_days, __set_ignore_last_n_days, None, None)

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

    def plot_covid_19_data(self, name):

        import matplotlib.pyplot as plt
        plt.rcParams['figure.figsize'] = [25, 4]

        assert name == 'combined'

        if name == 'combined':
            # Combine all column data in the surge
            plot_cases      = np.sum(self.cases,axis=1)
            plot_population = np.sum(self.populations)

        # Select data with non-zero cases only
        (nz_cases_ids,) = np.where(self.cases>0)
        plot_cases = np.copy(self.cases[nz_cases_ids])
        plot_dates = np.copy(self.dates[nz_cases_ids])

        # Drop days from the back if any

        deaths_100k_y = round(plot_cases[-1]*100000/plot_population * 365/plot_dates.size,1)

        xlabel = 'Date'
        ylabel = 'Cumulative Deaths []'

        place = 'US'
        title = 'COVID-19 in '+place+'; population: '+str(plot_population)+\
                '; deaths per 100k/y: '+str(deaths_100k_y)
        source = 'Johns Hopkins CSSE: https://github.com/CSSEGISandData/COVID-19'

        fig, ax = plt.subplots(figsize=(20,6))

        ax.plot( range(len(plot_dates)), cases, 'r*', label=legend )

        plt.xticks( range(len(plot_dates)), plot_dates, rotation=60, fontsize=14 )

        ax.set_ylabel(ylabel,fontsize=16)
        ax.set_xlabel(xlabel,fontsize=16)

        fig.suptitle(title,fontsize=20)
        plt.legend(loc='best',fontsize=12)
        plt.grid(True)
        plt.savefig('covid_19_data'+'.png', dpi=300)
        plt.show()

        return

    def fit_data(self, name ):

        assert name == 'combined'

        from chen_3170.toolkit import sigmoid_func
        from chen_3170.toolkit import grad_p_sigmoid_func
        from chen_3170.toolkit import sigmoid_func_prime
        from chen_3170.toolkit import sigmoid_func_double_prime
        from chen_3170.toolkit import newton_nlls_solve

        scaling = self.cases.max()
        self.cases /= scaling

        a0 = self.cases[-1]
        a1 = a0/self.cases[0] - 1
        a2 = -0.15

        param_vec_0 = np.array([a0,a1,a2])

        times = np.array(range(self.dates.size),dtype=np.float64)

        k_max = 25
        rel_tol = 0.01 / 100.0 # (0.01%)

        (param_vec,r2,k) = __newton_nlls_solve( times, self.cases,
                           sigmoid_func, grad_p_sigmoid_func,
                           param_vec_0, k_max, rel_tol, verbose=False )

        assert param_vec[0] > 0.0
        assert param_vec[1] > 0.0
        assert param_vec[2] < 0.0

        param_vec[0] *= scaling
        self.cases   *= scaling

        print('')
        print('Unscaled root =',param_vec)

        return param_vec

    def plot_covid_19_nlfit(self, name, 
            dates, deaths, fit_func, param_vec, 
            fit_func_prime=None, time_max_prime=None,
            fit_func_double_prime = None, time_min_max_double_prime=None,
            option='dates', ylabel='null-ylabel',
            legend='null-legend', title='null-title', formula='null-formula'):

        assert name == 'combined'

        import matplotlib.pyplot as plt

        plt.rcParams['figure.figsize'] = [20, 8]
        plt.figure(1)

        if option == 'dates':
            plt.plot(dates, deaths,'r*',label='experimental')
        elif option == 'days':
            plt.plot(range(len(dates)), deaths,'r*',label='experimental')

        import math
        import numpy as np

        n_plot_pts = 100
        dates_plot = np.linspace( 0, range(len(dates))[-1], n_plot_pts)

        cases_plot = fit_func( dates_plot, param_vec )

        plt.plot( dates_plot,cases_plot,'b-',label='NLS fitting' )

        if option == 'dates':
            plt.xticks( range(len(dates)),dates,rotation=60,fontsize=14)
            plt.xlabel(r'Date',fontsize=16)
        elif option == 'days':
            plt.xlabel(r'Time [day]',fontsize=16)
        else:
            assert False

        plt.ylabel(ylabel,fontsize=16)
        plt.title(title,fontsize=20)

        if time_max_prime is not None:

            cases = fit_func(time_max_prime,param_vec)
            plt.plot(time_max_prime, cases,'*',color='green',markersize=16)

            (x_min,x_max) = plt.xlim()
            dx = abs(x_max-x_min)
            x_text = time_max_prime - dx*0.15

            (y_min,y_max) = plt.ylim()
            dy = abs(y_max-y_min)
            y_text = cases + dy*0.00

            plt.text(x_text, y_text, r'(%3.2f, %1.3e)'%(time_max_prime,cases),
                fontsize=16)

        if time_min_max_double_prime is not None:

            t_min = time_min_max_double_prime[0]
            t_max = time_min_max_double_prime[1]

            cases = fit_func(t_max,param_vec)
            plt.plot(t_max, cases,'*',color='orange',markersize=16)

            (x_min,x_max) = plt.xlim()
            dx = abs(x_max-x_min)
            x_text = t_max - dx*0.15

            (y_min,y_max) = plt.ylim()
            dy = abs(y_max-y_min)
            y_text = cases + dy*0.00

            plt.text(x_text, y_text, r'(%3.2f, %1.3e)'%(t_max,cases),
                fontsize=16)

            cases = fit_func(t_min,param_vec)
            plt.plot(t_min, cases,'*',color='orange',markersize=16)

            (x_min,x_max) = plt.xlim()
            dx = abs(x_max-x_min)
            x_text = t_min - dx*0.15

            (y_min,y_max) = plt.ylim()
            dy = abs(y_max-y_min)
            y_text = cases + dy*0.00

            plt.text(x_text, y_text, r'(%3.2f, %1.3e)'%(t_min,cases),
                fontsize=16)

        (x_min,x_max) = plt.xlim()
        dx = abs(x_max-x_min)
        x_text = x_min + dx*0.07

        (y_min,y_max) = plt.ylim()
        dy = abs(y_max-y_min)
        y_text = y_min + dy*0.5

        plt.text(x_text, y_text, formula,fontsize=16)

        for (i,p) in enumerate(param_vec):
            y_text -= dy*0.1
            plt.text(x_text, y_text, r'$\alpha_{%i}$=%8.2e'%(i,p),fontsize=16)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(loc='best',fontsize=12)
        plt.grid(True)
        plt.show()

        if fit_func_prime is not None:

            plt.rcParams['figure.figsize'] = [20, 5]
            plt.figure(2)

            n_rows = 1
            n_cols = 2
            plt.subplot(n_rows,n_cols,1)

            n_plot_pts = 100
            dates_plot = np.linspace( 0, range(len(dates))[-1], n_plot_pts)

            cases_plot = fit_func_prime( dates_plot, param_vec )

            plt.plot(dates_plot,cases_plot,'b-',label='Fitting derivative' )

            if time_max_prime is not None:

                peak = fit_func_prime(time_max_prime,param_vec)
                plt.plot(time_max_prime, peak,'*',color='green',markersize=16)

                (x_min,x_max) = plt.xlim()
                dx = abs(x_max-x_min)
                x_text = time_max_prime - dx*0.35

                (y_min,y_max) = plt.ylim()
                dy = abs(y_max-y_min)
                y_text = peak + dy*0.00

                plt.text(x_text, y_text, r'(%3.2f, %1.3e)'%(time_max_prime,peak),
                    fontsize=14)

            plt.ylabel('Surge Speed [case/day]',fontsize=16)
            plt.grid(True)

            if fit_func_double_prime is not None:

                plt.subplot(n_rows,n_cols,2)

                n_plot_pts = 100
                dates_plot = np.linspace( 0, range(len(dates))[-1], n_plot_pts)

                cases_plot = fit_func_double_prime( dates_plot, param_vec )

                plt.plot(dates_plot,cases_plot,'b-',label='Fitting derivative' )

                if time_min_max_double_prime is not None:

                    t_min = time_min_max_double_prime[0]
                    t_max = time_min_max_double_prime[1]

                    max = fit_func_double_prime(t_max,param_vec)
                    plt.plot(t_max, max,'*',color='orange',markersize=16)

                    (x_min,x_max) = plt.xlim()
                    dx = abs(x_max-x_min)
                    x_text = t_max - dx*0.35

                    (y_min,y_max) = plt.ylim()
                    dy = abs(y_max-y_min)
                    y_text = max + dy*0.00

                    plt.text(x_text, y_text, r'(%3.2f, %1.3e)'%(t_max,max),
                        fontsize=14)

                    min = fit_func_double_prime(t_min,param_vec)
                    plt.plot(t_min, min,'*',color='orange',markersize=16)

                    (x_min,x_max) = plt.xlim()
                    dx = abs(x_max-x_min)
                    x_text = t_min - dx*0.35

                    (y_min,y_max) = plt.ylim()
                    dy = abs(y_max-y_min)
                    y_text = min + dy*0.00

                    plt.text(x_text, y_text, r'(%3.2f, %1.3e)'%(t_min,min),
                        fontsize=14)

                plt.ylabel('Surge Acceleration [case/day$^2$]',fontsize=16)
                plt.grid(True)

            plt.show()

        return

    def __sigmoid_func(self, x, param_vec):

        import numpy as np

        a0 = param_vec[0]
        a1 = param_vec[1]
        a2 = param_vec[2]

        f_x = a0 / ( 1 + a1 * np.exp(a2*x) )

        return f_x

    def __sigmoid_func_prime(self, x, param_vec):

        import numpy as np

        a0 = param_vec[0]
        a1 = param_vec[1]
        a2 = param_vec[2]

        f_x = a0 / ( 1 + a1 * np.exp(a2*x) )
        g_x = (-1) * a1 * a2 * np.exp(a2*x) / ( 1.0 + a1 * np.exp(a2*x) )

        fprime = g_x * f_x

        return fprime

    def __sigmoid_func_double_prime(self, x, param_vec):

        import numpy as np

        a0 = param_vec[0]
        a1 = param_vec[1]
        a2 = param_vec[2]

        f_x = a0 / ( 1 + a1 * np.exp(a2*x) )
        g_x = (-1) * a1 * a2 * np.exp(a2*x) / ( 1.0 + a1 * np.exp(a2*x) )
        g_prime_x = (-1) * a1 * a2**2 * np.exp(a2*x) / (1.0 + a1 * np.exp(a2*x) )**2

        double_prime = (g_prime_x + g_x**2 ) * f_x

        return double_prime

    def __grad_p_sigmoid_func(self, x, param_vec):

        import numpy as np

        a0 = param_vec[0]
        a1 = param_vec[1]
        a2 = param_vec[2]

        grad_p_f = np.zeros(param_vec.size, dtype=np.float64)

        grad_p_f_0 =   1./( 1. + a1 * np.exp(a2*x) )
        grad_p_f_1 = - a0/( 1. + a1 * np.exp(a2*x) )**2 * np.exp(a2*x)
        grad_p_f_2 = - a0/( 1. + a1 * np.exp(a2*x) )**2 * a1 * x*np.exp(a2*x)

        return (grad_p_f_0, grad_p_f_1, grad_p_f_2)

    def __newton_nlls_solve(self, x_vec, y_vec, fit_func, grad_p_fit_func, 
                      param_vec_0,
                      k_max=10, rel_tol=1.0e-3, verbose=True ):

        assert x_vec.size == y_vec.size

        import numpy as np
        import numpy.linalg

        try:
            from chen_3170.toolkit import solve
        except ModuleNotFoundError:
            assert False, 'You need to provide your own solve function here. Bailing out.'

        # Other initialization
        delta_vec_k = np.ones(param_vec_0.size, dtype=np.float64)*1e10
        r_vec_k     = np.ones(x_vec.size, dtype=np.float64)*1e10
        j_mtrx_k    = np.ones((x_vec.size,param_vec_0.size),dtype=np.float64)*1e10
        param_vec   = np.copy(param_vec_0)

        if verbose is True:
            print('\n')
            print('**************************************************************************')
            print("                      Newton's Method Iterations                          ")
            print('**************************************************************************')
            print('k  ||r(p_k)||  ||J(p_k)||  ||J^T r(p_k)||  ||del p_k||   ||p_k||  |convg| ')
            print('--------------------------------------------------------------------------')
        #         1234567890 12345678901 123456789012345 123456789012 123456789 12345678

        import math
        assert k_max >= 1
        k = 1

        while (np.linalg.norm(delta_vec_k/param_vec) > rel_tol or np.linalg.norm(j_mtrx_k.transpose()@r_vec_k) > 1e-3 ) and k <= k_max:

            # build the residual vector
            r_vec_k = y_vec - fit_func(x_vec, param_vec)

            # build the Jacobian matrix
            grad_p_f = grad_p_fit_func(x_vec, param_vec)

            j_mtrx_k = np.zeros( (x_vec.size, param_vec.size), dtype=np.float64 ) # initialize matrix
            for (i,grad_p_f_i) in enumerate(grad_p_f):
                j_mtrx_k[:,i] = - grad_p_f_i

            delta_vec_k_old = np.copy(delta_vec_k)

            rank = numpy.linalg.matrix_rank(j_mtrx_k.transpose()@j_mtrx_k)

            if rank != param_vec.size and verbose == True:
                print('')
                print('*********************************************************************')
                print('                             RANK DEFICIENCY')
                print('*********************************************************************')
                print('rank(JTJ) = %3i; shape(JTJ) = (%3i,%3i)'%
                      (rank, (j_mtrx_k.transpose()@j_mtrx_k).shape[0],
                             (j_mtrx_k.transpose()@j_mtrx_k).shape[1]))
                print('JTJ = ',j_mtrx_k.transpose()@j_mtrx_k)
                print('*********************************************************************')
                print('')

            if rank == param_vec.size:
                delta_vec_k = numpy.linalg.solve( j_mtrx_k.transpose()@j_mtrx_k,
                                                 -j_mtrx_k.transpose()@r_vec_k )
            #delta_vec_k = solve( j_mtrx_k.transpose()@j_mtrx_k, -j_mtrx_k.transpose()@r_vec_k,
            #                     pivoting_option='complete', pivot_tol=1e-5, zero_tol=1e-10)
            else:
                a_mtrx_k = j_mtrx_k.transpose()@j_mtrx_k
                b_vec_k  = -j_mtrx_k.transpose()@r_vec_k
                delta_vec_k = numpy.linalg.solve(
                       a_mtrx_k.transpose()@a_mtrx_k + 1e-3*np.eye(param_vec.size),
                       a_mtrx_k.transpose()@b_vec_k )

            r_vec_k_old = np.copy(r_vec_k)
            step_size = 1.0
            r_vec_k = y_vec - fit_func( x_vec, param_vec + delta_vec_k )

            n_steps_max = 5
            n_steps = 0
            while (np.linalg.norm(r_vec_k) > np.linalg.norm(r_vec_k_old)) and n_steps <= n_steps_max:
                step_size *= 0.5
                r_vec_k = y_vec - fit_func( x_vec, param_vec + step_size*delta_vec_k )
                n_steps += 1

            if step_size != 1.0 and verbose is True:
                print('Step_size = ',step_size,' n_steps = ',n_steps,
                        ' n_steps_max = ',n_steps_max)

            # compute the update to the root candidate
            param_vec += step_size * delta_vec_k

            if k > 0:
                if np.linalg.norm(delta_vec_k) != 0.0 and np.linalg.norm(delta_vec_k_old) != 0.0:
                    convergence_factor = math.log(np.linalg.norm(delta_vec_k),10) / math.log(np.linalg.norm(delta_vec_k_old),10)
                else:
                    convergence_factor = 0.0
            else:
                convergence_factor = 0.0

            if verbose is True:
                print('%2i %+10.2e %+11.2e %+15.2e %+12.2e %+9.2e %8.2f'%\
                    (k,np.linalg.norm(r_vec_k),np.linalg.norm(j_mtrx_k),
                       np.linalg.norm(j_mtrx_k.transpose()@r_vec_k),
                       np.linalg.norm(delta_vec_k), np.linalg.norm(param_vec),
                       convergence_factor) )

            k = k + 1

        r2 = 1.0 - np.sum(r_vec_k**2) / np.sum((y_vec-np.mean(y_vec))**2 )

        if verbose is True:
            print('******************************************************')
            print('Root = ',param_vec)
            print('R2   = ',r2)

        if k > k_max:
            print('')
            print('******************************************************')
            print('WARNING: Convergence failure k > k_max                ')
            print('******************************************************')
            print('')

        return (param_vec, r2, k)

    def critical_times(self, name, param_vec):

        assert name == 'combined'

        ( time_max_prime, prime_max ) = self. __sigmoid_prime_max(param_vec)

        if time_max_prime%1:
            time_max_id = int(time_max_prime) + 1
        else:
            time_max_id = int(time_max_prime)

        print('Maximum growth rate            = %3.2e [death/day]'%(prime_max))
        print('Maximum normalized growth rate = %3.2e [%%/day]'%(prime_max/a0*100))
        print('Time at maximum growth rate    = %3.1f [day]'%(time_max_prime))
        if time_max_id > dates.size-1:
            print('WARNING: Ignore maximum growth rate; time at max. growth exceeds time length.')
        else:
            print('Date at maximum growth rate = %s '%(self.dates[time_max_id]))

        print('')

        time_max_double_prime = -math.log(a1/(2+math.sqrt(3)))/a2 # time at maximum growth acceleration

        if time_max_double_prime%1:
            time_max_id = int(time_max_double_prime) + 1
        else:
            time_max_id = int(time_max_double_prime)

        assert abs( a0*a2**2*(5+3*math.sqrt(3))/(3+math.sqrt(3))**3 - sigmoid_func_double_prime(time_max_double_prime,param_vec) ) <= 1.e-8

        print('Maximum growth acceleration            = %3.2e [death/day^2]'%(a0*a2**2*(5+3*math.sqrt(3))/(3+math.sqrt(3))**3))
        print('Maximum normalized growth acceleration = %3.2e [%%/day^2]'%(a2**2*(5+3*math.sqrt(3))/(3+math.sqrt(3))**3*100))
        print('Time at maximum growth accel.          = %3.1f [day]'%(time_max_double_prime))
        print('Shifted time at maximum growth accel.  = %3.1f [day]'%(time_max_double_prime-time_max_prime))
        if time_max_id > dates.size-1:
            print('WARNING: Ignore maximum growth accel.; time at max. growth accel. exceeds time length.')
        else:
            print('Date at maximum growth accel. = %s '%(dates[time_max_id]))

        print('')

        time_min_double_prime = -math.log(a1/(2-math.sqrt(3)))/a2 # time at minimum growth rate

        if time_min_double_prime%1:
            time_min_id = int(time_min_double_prime) + 1
        else:
            time_min_id = int(time_min_double_prime)

        assert abs(a0*a2**2*(5-3*math.sqrt(3))/(3-math.sqrt(3))**3 - sigmoid_func_double_prime(time_min_double_prime,param_vec)) <= 1.e-8

        print('')
        print('Minimum growth acceleration            = %3.2e [death/day^2]'%(a0*a2**2*(5-3*math.sqrt(3))/(3-math.sqrt(3))**3))
        print('Minimum normalized growth acceleration = %3.2e [%%/day^2]'%(a2**2*(5-3*math.sqrt(3))/(3-math.sqrt(3))**3*100))
        print('Time at minimum growth accel.          = %3.1f [day]'%(time_min_double_prime))
        print('Shifted time at maximum growth accel.  = %3.1f [day]'%(time_min_double_prime-time_max_prime))
        if time_min_id > dates.size-1:
            print('WARNING: Ignore maximum growth accel.; time at min. growth accel. exceeds time length.')
        else:
            print('Date at minimum growth accel. = %s '%(self.dates[time_min_id]))

        print('')
        print('Surge period = %3.2e [day]'%(time_min_double_prime-time_max_double_prime))

        assert abs( (time_max_prime-time_max_double_prime) - (time_min_double_prime - time_max_prime) ) <= 1.e-5

        return ( time_max_prime, time_max_prime-time_max_double_prime )

    def __sigmoid_prime_max(self, param_vec):

        a0 = param_vec[0]
        a1 = param_vec[1]
        a2 = param_vec[2]

        tc = -math.log(a1)/a2 # time at maximum growth rate

        prime_max = -a0*a2/4.0

        assert abs(prime_max - self.__sigmoid_func_prime(tc,param_vec)) <= 1.e-8

        return (tc, prime_max)

    def __sigmoid_double_prime_max(self, param_vec):

        a0 = param_vec[0]
        a1 = param_vec[1]
        a2 = param_vec[2]

        time_max_double_prime = -math.log(a1/(2+math.sqrt(3)))/a2 # time at maximum growth acceleration

        assert abs( a0*a2**2*(5+3*math.sqrt(3))/(3+math.sqrt(3))**3 - sigmoid_func_double_prime(time_max_double_prime,param_vec) ) <= 1.e-8
