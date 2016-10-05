# Use some existing time series data to test PCTLc logic by Samantha Kleinberg
# Fix the window time here ( |r - s| is fixed here).

import numpy as np
import matplotlib.pyplot as plt
import pylab
import pickle
import os
import pandas as pd
import statsmodels.tsa.api as sta
import math
import statsmodels.tsa.stattools as sts
from datetime import datetime
import time
import math
import statistics as st
import statsmodels.stats.stattools as ssts
import seaborn
import itertools

class DataProcess:
    def __init__(selfself, mfile, tfile):
        measure_file_path = 'F://Github//Causality-Prediction//data//measure_series//inhib//v2'
        steep_inhib_times = pickle.load(
            open('F://Inhibition//VAR_causality//data_files//steep_inhib_times.pickle', 'rb'))


class TLogic:
    def __init__(self, data, measures):
        self.cascade_df = data
        self.measures = measures

    def dynamic_intervals(self, start, delta_t):
        mean_series = np.mean(self.cascade_df[self.measures[0]])
        startPoint = 0
        endPoint = 0
        dnIntervals = []
        while endPoint < len(self.cascade_df[self.measures[0]]):
            if self.cascade_df[self.measures[0]][endPoint] >= mean_series:
                endPoint += 1
            else:
                tInt = (startPoint, endPoint)
                dnIntervals.append(tInt)
                endPoint += 1
                startPoint = endPoint

        print(self.cascade_df)

    def rules_formulas(self, delta_t, lag):
        mean_measure_value = np.mean(self.cascade_df[self.measures[0]]) / 2
        startPoint = 0
        endPoint = startPoint + delta_t
        dnIntervals = []
        while endPoint < len(self.cascade_df[self.measures[0]]):
            # check for statisfaction of formula 1
            while startPoint < endPoint:
                if self.cascade_df[self.measures[0]][endPoint] < mean_measure_value:
                    startPoint = endPoint+1
                    endPoint += 1
                    break

            # check for satisfaction of formula 2
            if startPoint == endPoint:
                



if __name__ == '__main__':
    measure_file_path = 'F://Github//Causality-Prediction//data//measure_series//inhib//v2'
    steep_inhib_times = pickle.load(open('F://Inhibition//VAR_causality//data_files//steep_inhib_times.pickle', 'rb'))

    dependent_variables = []
    # print(cascade_int_time)

    # Load the measure files
    cnt_measures = 0
    model_df = pd.DataFrame()
    control_variables = {}
    dependent_variables = {}

    measures = []
    model_order = 10
    f_list_null = []
    p_list_null = []

    f_list_full = []
    p_list_full = []
    measure_time_df = []

    for files in os.listdir(measure_file_path):
        full_path = measure_file_path + '//' + files
        mname = files[:len(files)-7]
        measure_time_df.append(pickle.load(open(full_path, 'rb')))
        measures.append(mname)

    statistic_values = {}
    p_values = {}
    critical_values = {}
    granger_cause_count = {}

    for L in range(0, 2):
        for subset in itertools.combinations(range(len(measures)), L):
            num_measures = len(subset)
            if num_measures == 0:
                continue
            measure_series = []
            cascade_df_feat = pd.DataFrame()
            cnt_mids = 0
            for mid in measure_time_df[0]:
                steep_time = pd.to_datetime(steep_inhib_times[mid]['steep'])
                inhib_time = pd.to_datetime(steep_inhib_times[mid]['decay'])
                # print(inhib_time)
                # Combine all the features in a dataframe for sorting them by time.
                cascade_df = measure_time_df[0][mid]
                cascade_df_feat['time'] = pd.to_datetime(cascade_df['time'])
                cascade_df_feat['time'] = pd.to_datetime(cascade_df['time'])

                for idx in range(num_measures):
                    # if measures[subset[idx]] == 'bw' or measures[subset[idx]] == 'cc':
                    cascade_df_feat[measures[subset[idx]]] = measure_time_df[subset[idx]][mid][measures[subset[idx]]]
                cascade_df_feat = cascade_df_feat.sort('time')
                #cascade_df_feat = cascade_df_feat[cascade_df_feat['time'] < pd.to_datetime(inhib_time)]

                # print(cascade_df_eat)
                time_series = list(cascade_df_feat['time'])
                measure_series_all = []
                for idx in range(num_measures):
                    measure_series_all.append(list(cascade_df_feat[measures[subset[idx]]]))

                Y_act = [0 for idx in range(len(time_series))]
                Y_time = []

                for idx in range(1, len(time_series)):
                    rt_time = str(time_series[idx])
                    rt_date = rt_time[:10]
                    rt_t = rt_time[11:19]
                    record_time = rt_date + ' ' + rt_t
                    time_x = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                    cur_time = time.mktime(time_x.timetuple())

                    rt_time = str(time_series[idx-1])
                    rt_date = rt_time[:10]
                    rt_t = rt_time[11:19]
                    record_time = rt_date + ' ' + rt_t
                    time_x = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                    prev_time = time.mktime(time_x.timetuple())

                    Y_act[idx] = (cur_time - prev_time)/60

                X = [[] for i in range(len(subset))]
                Y = []
                time_new = []
                measures_ratios = [[] for i in range(len(subset))]
                # Remove the time_series rows with values of \delta t=0
                for idx in range(len(Y_act)):
                    # if Y_act[idx] == 0 and idx > 0:
                    #     continue
                    # measures_ratios[idx_sub].append(1)
                    for idx_sub in range(len(subset)):
                        X[idx_sub].append(measure_series_all[idx_sub][idx])
                        if idx > 0:
                            measures_ratios[idx_sub].append(measure_series_all[idx_sub][idx] / measure_series_all[idx_sub][idx-1])
                        else:
                            measures_ratios[idx_sub].append(1)
                        # print(measures_ratios[idx_sub])
                    Y.append(Y_act[idx])
                    time_new.append(time_series[idx])


                cascade_ts_df = pd.DataFrame()
                cascade_ts_df['time_diff'] = Y
                cascade_ts_df.index = time_new
                for idx_sub in range(len(subset)):
                    cascade_ts_df[measures[subset[idx_sub]]] = X[idx_sub]
                    cascade_ts_df[measures[subset[idx_sub]] + '_ratios'] = measures_ratios[idx_sub]
                s = cascade_ts_df.shape
                cascade_ts_df = cascade_ts_df.fillna(0)

                # print(cascade_ts_df)
                # print(cascade_ts_df.shape)
                # Step 3: Remove the NaN values from the df.
                # Y_diff = []
                # X_diff = [[] for i in range(len(subset))]
                # for idx in range(len(Y)):
                #     if np.isnan(Y[idx]):
                #        continue
                #     Y_diff.append(Y[idx])
                #     for idx_sub in range(len(subset)):
                #         X_diff[idx_sub].append(X[idx_sub][idx])

                # X = np.asarray(X_diff)
                # Y = np.asarray(Y_diff)
                #
                # cascade_VAR_df = pd.DataFrame()
                # cascade_VAR_df['time_diff'] = Y
                # for idx_sub in range(len(subset)):
                #     cascade_VAR_df[measures[subset[idx_sub]]] = X[idx_sub,:]

                # measures_causality = []
                # measures_string = ''
                # for idx_sub in range(len(subset)):
                #     measures_causality.append(measures[subset[idx_sub]])
                #     measures_string += (measures[subset[idx_sub]] + ' + ')
                # measures_string = measures_string[:len(measures_string) - 3]

                # print(cascade_ts_df)

                # plt.plot(range(len(cascade_ts_df.index)), cascade_ts_df['pr_ratios'])
                # plt.show()
                temporal_logic = TLogic(cascade_ts_df, measures)
                temporal_logic.dynamic_intervals(0, 1)

                cnt_mids += 1
                if cnt_mids > 0:
                    break