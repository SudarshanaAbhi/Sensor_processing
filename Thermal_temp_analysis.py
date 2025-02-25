#Abhi S.: extract temp log files based on data

import csv
import numpy as np 

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.signal import find_peaks

# Read the Excel file
file = "C:/Users/Abhinand/Desktop/TMB02010_edit.csv" #"C:\Users\Abhinand\Desktop\TMB02009_edit.csv" ""C:\Users\Abhinand\Desktop\TMB02009_update.xlsx"" ""C:\Users\Abhinand\Desktop\TMB02010_edit.csv""
df = pd.read_csv(file)

# Function to extract chunks between headers
def extract_data_chunks(df):

    # only keep value columns  
    df_update = df.loc[:, df.columns.str.contains('value', case=False)]

    # Find rows with column headers
    #header_rows = df[df.apply(lambda row: any(str(cell).lower() == 'value' for cell in row), axis=1)].index.tolist()
    header_rows = df_update[df_update.apply(lambda row: row.astype(str).str.contains('value', case=False).any(), axis=1)].index.tolist()

    # Sort header indices to ensure they're in order
    header_rows.sort()
    
    # Extract data between headers
    for i in range(len(header_rows)):
        # Get start and end indices
        start = header_rows[i]   # Start after the header row
        end = header_rows[i+1] if i+1 < len(header_rows) else len(df_update)
        
        ans_dataset = input(f'Analyze start row {start} dataset? y or n: ')
        if ans_dataset == 'n':
            continue

        # Extract the chunk
        subset_df = df_update.iloc[start:end].copy()
        
        # Remove rows with non-numeric values
        subset_df = subset_df.apply(pd.to_numeric, errors='coerce')
        subset_df = subset_df.dropna(how = 'any')

        # Optional: Use the header row to set column names
        #chunk.columns = dataframe.iloc[header_rows[i]]
        col_100_val = list((subset_df > 100).any())
        
        if sum(col_100_val) == 1:
            # Filter out columns with values greater than 100 
            subset_df = subset_df.loc[:, (subset_df <= 100).all()]

        subset_df.columns = ['L1:inlet', 'L1:middle', 'L1:outlet', 'L2:inlet', 'L2:outlet', 'L3:inlet', 'L3:middle', 'L3:outlet', 'L4:inlet', 'L4:middle', 'L4:outlet']

        ax = subset_df.plot(figsize=(15, 8))
        # Add title and labels
        plt.title('Thermal FC data')
        plt.xlabel('Time (s)')
        plt.ylabel('Temp (C)')  # Set the y-axis label
        plt.grid(True)

        ax.legend(title='probes', loc='best')

        # Show the plot
        plt.show()
        
        # Dataframe to gather all avg rcovery times for all probes for a dataset 
        # df_rec_time = pd.DataFrame()

        # Dataframe to gather all avg min temp values for all probes for a dataset 
        # df_min_temp = pd.DataFrame()

        # Local maxima for each probe data
        for probe_name in subset_df.columns:
            
            ans = input(f'Analyze {probe_name} data for start row {start} dataset? y or n: ')
            if ans == 'n':
                continue  

            probe_val = pd.DataFrame(subset_df.loc[:, [f'{probe_name}']])

            # Manually find the local max where temp drops

            plt.plot(probe_val, label=f"{probe_name}", color='b')

            drop_start_pnts_idx = []
            temp_rec_endpnts = []

            def find_temp_drop_pnts():
                
                idx = 5
                end_idx = len(probe_val)
                left_crit = 0.5
                right_crit = 1

                if 'out' in probe_name:
                    left_crit = 0.4
                    right_crit = 0.4

                #for idx in range(start_idx, len(probe_val)):
                while idx < end_idx - 5:
    
                    val = probe_val.iloc[idx,0]
                    
                    #if (idx > start_idx) and (idx < end_idx):
                    left = idx - 2 
                    right = idx + 3 

                    if abs(val - probe_val.iloc[left, 0]) < left_crit and (val - probe_val.iloc[right, 0]) > right_crit:     
                        drop_start_pnts_idx.append(idx)
                        wind_idx_end = idx + 5
                    else:
                        idx += 1 
                        continue 
                    #while (idx < wind_idx_end) and (wind_idx_end < end_idx):
                    while wind_idx_end < end_idx:
                        #wind_idx_end += 1
                        if (probe_val.iloc[idx, 0] - probe_val.iloc[wind_idx_end, 0]) < 0.5:
                            temp_rec_endpnts.append(wind_idx_end)
                            idx = wind_idx_end + 5
                            break
                        else: 
                            wind_idx_end += 1                          
                            continue
                    else:
                        break


            find_temp_drop_pnts()


            asp_vol = [50, 100, 200]
            asp_50_time = (50 * 60) / 2000  # assuming 2ml/min
            asp_100_time = (100 * 60) / 2000  # assuming 2ml/min
            asp_200_time = (200 * 60) / 2000  # assuming 2ml/min
  
            # Convert all temp drop start pnts and rec time endpoints into actual time values
            real_begin_idx = drop_start_pnts_idx + probe_val.index[0]
            real_end_idx = temp_rec_endpnts + probe_val.index[0]
            # Real time values
            real_time_begin = df.loc[real_begin_idx, 'Time']
            real_time_end = df.loc[real_end_idx, 'Time']

            # Calc rec time for each corresponding begin and end time values
            time_format = "%H:%M:%S"  
            time_val_begin = [datetime.strptime(time, time_format) for time in list(real_time_begin)]
            time_val_end = [datetime.strptime(time, time_format) for time in list(real_time_end)]                                 
            rec_time = []
            for i in range(len(list(time_val_end))):
                rec_time.append((time_val_end[i] - time_val_begin[i]).total_seconds())
            
            # Compensate for aspiration time 
            rec_time_update = [i - asp_200_time for i in rec_time]

            possible_temps = [37, 45, 50, 60, 65, 75]
            # possible_temps = [40, 45, 60, 75]
            rec_time_dict = {}

            min_length = min(len(drop_start_pnts_idx), len(rec_time_update))
            drop_start_pnts_idx = drop_start_pnts_idx[:min_length]
            rec_time_update = rec_time_update[:min_length]

            def create_temp_rec_dict():
                # Store values in dictionary based on set point temp

                for meas_temp_idx in drop_start_pnts_idx:
                    meas_temp = probe_val.iloc[meas_temp_idx, 0]
                    # print(meas_temp)

                    for temp in possible_temps:

                        threshold = 4 if temp >= 50 else 2.8

                        if (abs(meas_temp - temp) <= threshold): # and (meas_temp < temp):
                            # Initialize list for the temp if it doesn't exist
                            if temp not in rec_time_dict:
                                rec_time_dict[temp] = []
                            # find corresponding index of the temp to the recovery time
                            idx_num = drop_start_pnts_idx.index(meas_temp_idx)
                            curr_rec_time = rec_time_update[idx_num] 
                            # Add to the list for this temperature
                            rec_time_dict[temp].append(curr_rec_time)

            create_temp_rec_dict()

            print(f'recovery time data for {probe_name}:')
            for key, value in rec_time_dict.items():
                print(f"{key}: {value}")

            # Average the recovery time values for each set point temp
            # rec_time_dict_avg = {}
            # global rec_time_avg_list
            # rec_time_avg_list = []
            # for key, values in rec_time_dict.items():
                # avg = sum(values) / len(values)
                # rec_time_dict_avg[key] = avg
                # rec_time_avg_list.append(avg)

            # add avg rec times for the probe to the dataframe  
            # df_rec_time[f'{probe_name}'] = rec_time_avg_list
            # print(df_rec_time)


            plt.plot(probe_val, label=f"{probe_name}", color='b')
            pks_max_upd = []
            for i in drop_start_pnts_idx:
                pks_max_upd.append(i + probe_val.index[0])

            rec_end_upd = []
            for i in temp_rec_endpnts:
                rec_end_upd.append(i + probe_val.index[0])

            plt.scatter(pks_max_upd, probe_val.iloc[drop_start_pnts_idx, 0], color='r', label='start temp')
            plt.scatter(rec_end_upd, probe_val.iloc[temp_rec_endpnts, 0], color='g', label='end temp')
            plt.title(f'{probe_name}')
            plt.show()

            # Calc lowest temp reached during aspiration using min peaks
            
            mintemp_dict = {} 
              
            pks_min = find_peaks((-1)*(probe_val.iloc[:,0]), prominence=.8); #Prom: values between 0 and 1 (can modify value); closer to 0 means all peaks; closer to 1 means only strong peaks 
            pks_min_idx = list(pks_min[0]);
            #pks_min_timevals = [x / 10 for x in pks_min_list];
            plt.plot(probe_val, label=f"{probe_name}", color='b')
            pks_min_upd = []
            for i in pks_min_idx:
                pks_min_upd.append(i + probe_val.index[0])

            vals_to_plt = [probe_val.iloc[i, 0] for i in pks_min_idx]

            plt.scatter(pks_min_upd, vals_to_plt, color='r', label='min temp')
            plt.title(f'{probe_name}')
            plt.show()

            # add min temp values to the dataframe 
            mintemp_dict[f'{probe_name}'] = list(probe_val.iloc[pks_min[0], 0])

            # print(mintemp_dict)

            mintemp_dict_sorted = {}    

            def mintemp_dict_sort():
                # Store values in dictionary based on set point temp

                for min_idx in pks_min_idx:
                    # print(min_idx)
                    # print(type(min_idx))
                    min_temp = probe_val.iloc[min_idx, 0]

                    def match_drop_pts(min_idx, drop_pnts):

                        for max_pnt in drop_pnts:
                            if abs(min_idx - max_pnt) <= 20:
                                
                                meas_temp = probe_val.iloc[max_pnt, 0]
                                #meas_temp = meas_temp.iloc[0]
                                # print(meas_temp)  

                                for temp in possible_temps:
                
                                    threshold = 4 if temp >= 50 else 2.8

                                    if (abs(meas_temp - temp) <= threshold): # and (meas_temp < temp):
                                        # Initialize list for the temp inf it doesn't exist
                                        if temp not in mintemp_dict_sorted:
                                            mintemp_dict_sorted[temp] = []
                                        
                                        # Add to the list for this temperature
                                        mintemp_dict_sorted[temp].append(float(min_temp))            
                    
                    match_drop_pts(min_idx, drop_start_pnts_idx)
            
            mintemp_dict_sort()

            print()
            print(f'min temp data for {probe_name}:')
            for key, value in mintemp_dict_sorted.items():
                print(f"{key}: {value}")
            print()

            # Get average of min peaks based on temp set points 
            # global mintemp_dict_sort_avg
            # mintemp_dict_sort_avg = {}
            # min_temp_avg_list = []
            # for key, values in mintemp_dict_sorted.items():
            #     avg = sum(values) / len(values)
            #     mintemp_dict_sort_avg[key] = avg
            #     min_temp_avg_list.append(avg)

            # add avg rec times for the probe to the dataframe  
            # df_min_temp[f'{probe_name}'] = min_temp_avg_list
            # print(df_min_temp)

        # Save recovery time data and min temp data into a csv file for each dataset 
        # input('Save data to csv file? y for yes and n for no: ')
        # if str(input) == 'y':
        #     all_df = pd.DataFrame([df_rec_time, df_min_temp])
        #     all_df.to_csv(f'{start}_row_thermalFC_analysis.csv')


extract_data_chunks(df)
