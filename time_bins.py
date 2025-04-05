"""
Respiratory Data Processor
Time bins calculations module
"""

import pandas as pd
import numpy as np
import copy
from statistics import mean

def process_time_bins(zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list, intervals, number_of_breaths):
    """
    Process respiratory data using the time bins method
    
    Parameters:
    zeroed_time_list - List of time values with zero flow points
    zeroed_vol_list - List of volume values with zero flow points
    zeroed_flow_list - List of flow values with zero flow points
    phase_indexes_list - List of phase indexes
    intervals - Number of intervals to divide each breath into
    number_of_breaths - Number of breaths to process
    
    Returns:
    Dictionary with time bins data for each breath, average time bins data, and breath statistics
    """
    # Initiate Dictionaries for Time Bins
    time_bins_breath_dictionary = {}
    original_insp_data_breath_dictionary = {}
    original_exp_data_breath_dictionary = {}
    
    # Initiate Lists to calculate the tidal volume of each phase of each breath
    Vt_Insp_list = []
    Vt_Exp_list = []
    
    # Initiate Lists to calculate the total time of each phase of each breath
    Tt_Insp_list = []
    Tt_Exp_list = []
    
    # Process each breath
    for i in range(number_of_breaths):
        # Create new breath dictionaries
        Breath_Dict_Name = f"Breath_{i}"
        time_bins_breath_dictionary[Breath_Dict_Name] = {}
        original_insp_data_breath_dictionary[Breath_Dict_Name] = {}
        original_exp_data_breath_dictionary[Breath_Dict_Name] = {}
        
        # Separate inspiration data
        Insp_Time = []
        Time_subtract_value_insp = zeroed_time_list[0]
        phase_limit = 0
        
        # Extract inspiration time
        while phase_limit < phase_indexes_list[0]:
            zeroed_time_list[0] = zeroed_time_list[0] - Time_subtract_value_insp
            Insp_Time.append(zeroed_time_list[0])
            del zeroed_time_list[0]
            phase_limit += 1
        
        # Extract inspiration volume
        phase_limit = 0
        insp_vol = []
        while phase_limit < phase_indexes_list[0]:
            insp_vol.append(zeroed_vol_list[0])
            del zeroed_vol_list[0]
            phase_limit += 1
            
        # Extract inspiration flow
        phase_limit = 0
        Insp_Flow = []
        while phase_limit < phase_indexes_list[0]:
            Insp_Flow.append(zeroed_flow_list[0])
            del zeroed_flow_list[0]
            phase_limit += 1
            
        # Remove the first index
        del phase_indexes_list[0]
        
        # Separate expiration data
        phase_limit = 0
        Time_subtract_value_exp = zeroed_time_list[0]
        Exp_Time = []
        
        # Extract expiration time
        while phase_limit < phase_indexes_list[0]:
            zeroed_time_list[0] = zeroed_time_list[0] - Time_subtract_value_exp
            Exp_Time.append(zeroed_time_list[0])
            del zeroed_time_list[0]
            phase_limit += 1
            
        # Extract expiration volume
        phase_limit = 0
        Exp_Volume = []
        while phase_limit < phase_indexes_list[0]:
            Exp_Volume.append(zeroed_vol_list[0])
            del zeroed_vol_list[0]
            phase_limit += 1
            
        # Extract expiration flow
        phase_limit = 0
        Exp_Flow = []
        while phase_limit < phase_indexes_list[0]:
            Exp_Flow.append(zeroed_flow_list[0])
            del zeroed_flow_list[0]
            phase_limit += 1
            
        # Remove the first index
        del phase_indexes_list[0]
        
        # Store original data
        original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Time"] = Insp_Time
        original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Vol"] = insp_vol
        original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Flow"] = Insp_Flow
        original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Time"] = Exp_Time
        original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Vol"] = Exp_Volume
        original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Flow"] = Exp_Flow
        
        # Calculate total times and tidal volumes
        Tt_Insp_list.append(Insp_Time[-1])
        Tt_Exp_list.append(Exp_Time[-1])
        Vt_Insp = abs(insp_vol[-1] - insp_vol[0])
        Vt_Insp_list.append(Vt_Insp)
        Vt_Exp = abs(Exp_Volume[-1] - Exp_Volume[0])
        Vt_Exp_list.append(Vt_Exp)
        
        # Calculate time intervals
        insp_time_intervals_tbins = []
        incr_insp_time = Tt_Insp_list[i] / intervals
        for j in range(intervals + 1):
            Tt_insp_value = incr_insp_time * j
            insp_time_intervals_tbins.append(Tt_insp_value)
            
        exp_time_intervals_tbins = []
        incr_exp_time = Tt_Exp_list[i] / intervals
        for j in range(intervals + 1):
            Tt_exp_value = incr_exp_time * j
            exp_time_intervals_tbins.append(Tt_exp_value)
            
        # Interpolate values for Flow and Volume based on time intervals
        insp_vol_intervals_tbins = []
        insp_flow_intervals_tbins = []
        
        for j in range(len(insp_time_intervals_tbins)):
            Actual_Time_Interval = insp_time_intervals_tbins[j]
            for l in range(len(Insp_Time)):
                try:
                    if Actual_Time_Interval == 0:
                        insp_vol_intervals_tbins.append(insp_vol[0])
                        insp_flow_intervals_tbins.append(Insp_Flow[0])
                        break
                    elif Insp_Time[l] < Actual_Time_Interval < Insp_Time[l + 1]:
                        t1 = Insp_Time[l]
                        t2 = Insp_Time[l + 1]
                        v1 = insp_vol[l]
                        v2 = insp_vol[l + 1]
                        f1 = Insp_Flow[l]
                        f2 = Insp_Flow[l + 1]
                        
                        Volume_at_Interval = v1 + ((v2 - v1) / (t2 - t1)) * (Actual_Time_Interval - t1)
                        Flow_at_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Actual_Time_Interval - t1)
                        
                        insp_vol_intervals_tbins.append(Volume_at_Interval)
                        insp_flow_intervals_tbins.append(Flow_at_Interval)
                        break
                    elif Actual_Time_Interval == Insp_Time[-1]:
                        insp_vol_intervals_tbins.append(insp_vol[-1])
                        insp_flow_intervals_tbins.append(Insp_Flow[-1])
                        break
                except IndexError:
                    insp_vol_intervals_tbins.append(insp_vol[l])
                    insp_flow_intervals_tbins.append(Insp_Flow[l])
                    
        exp_vol_intervals_tbins = []
        exp_flow_intervals_tbins = []
        
        for j in range(len(exp_time_intervals_tbins)):
            Actual_Time_Interval = exp_time_intervals_tbins[j]
            for l in range(len(Exp_Time)):
                try:
                    if Actual_Time_Interval == 0:
                        exp_vol_intervals_tbins.append(Exp_Volume[0])
                        exp_flow_intervals_tbins.append(Exp_Flow[0])
                        break
                    elif Exp_Time[l] < Actual_Time_Interval and Exp_Time[l + 1] > Actual_Time_Interval:
                        t1 = Exp_Time[l]
                        t2 = Exp_Time[l + 1]
                        v1 = Exp_Volume[l]
                        v2 = Exp_Volume[l + 1]
                        f1 = Exp_Flow[l]
                        f2 = Exp_Flow[l + 1]
                        
                        Volume_at_Interval = v1 + ((v2 - v1) / (t2 - t1)) * (Actual_Time_Interval - t1)
                        Flow_at_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Actual_Time_Interval - t1)
                        
                        exp_vol_intervals_tbins.append(Volume_at_Interval)
                        exp_flow_intervals_tbins.append(Flow_at_Interval)
                        break
                    elif Actual_Time_Interval / Exp_Time[-1] == 1:
                        exp_vol_intervals_tbins.append(Exp_Volume[-1])
                        exp_flow_intervals_tbins.append(Exp_Flow[-1])
                        break
                except IndexError:
                    exp_vol_intervals_tbins.append(Exp_Volume[l])
                    exp_flow_intervals_tbins.append(Exp_Flow[l])
                    
        # Store time bins data
        time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Time"] = insp_time_intervals_tbins
        time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"] = insp_vol_intervals_tbins
        time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"] = insp_flow_intervals_tbins
        time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Time"] = exp_time_intervals_tbins
        time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"] = exp_vol_intervals_tbins
        time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"] = exp_flow_intervals_tbins
    
    # Copy the time bins dictionary for later use
    time_bin_copy = copy.deepcopy(time_bins_breath_dictionary)
    
    # Calculate the Mean shift value for normalization
    Mean_shift = 0
    for i in range(number_of_breaths):
        Subtraction_Value_insp = time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][-1]
        Mean_shift = Mean_shift + Subtraction_Value_insp
        for j in range(intervals + 1):
            time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j] = (
                time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j] - Subtraction_Value_insp
            )
        Subtraction_Value_exp = time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][0]
        Mean_shift = Mean_shift + Subtraction_Value_exp
        for j in range(intervals + 1):
            time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j] = (
                time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j] - Subtraction_Value_exp
            )
    
    Mean_shift = Mean_shift / (number_of_breaths * 2)
    
    # Normalize volume values as percentage of tidal volume
    Avg_Insp_Vt = mean(Vt_Insp_list)
    Avg_Exp_Vt = mean(Vt_Exp_list)
    
    for i in range(number_of_breaths):
        for j in range(intervals + 1):
            time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j] = (
                (time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j] / Vt_Insp_list[i]) * Avg_Insp_Vt
            )
        for j in range(intervals + 1):
            time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j] = (
                (time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j] / Vt_Exp_list[i]) * Avg_Exp_Vt
            )
    
    # Calculate average time bin data
    avg_insp_vol_tbin = []
    avg_exp_vol_tbin = []
    avg_insp_flow_tbin = []
    avg_exp_flow_tbin = []
    avg_insp_vol_tbin_sem = []
    avg_exp_vol_tbin_sem = []
    avg_insp_flow_tbin_sem = []
    avg_exp_flow_tbin_sem = []
    
    for j in range(intervals + 1):
        # Inspiration volume average
        Total_Insp_Volume = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j])
            Total_Insp_Volume += time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_insp_vol_tbin_sem.append(x)
        Avg_Insp_Vol = (Total_Insp_Volume / number_of_breaths) + Mean_shift
        avg_insp_vol_tbin.append(Avg_Insp_Vol)
        
        # Expiration volume average
        Total_Exp_Volume = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j])
            Total_Exp_Volume += time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_exp_vol_tbin_sem.append(x)
        Avg_Exp_Vol = (Total_Exp_Volume / number_of_breaths) + Mean_shift
        avg_exp_vol_tbin.append(Avg_Exp_Vol)
        
        # Inspiration flow average
        Total_Insp_Flow = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j])
            Total_Insp_Flow += time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_insp_flow_tbin_sem.append(x)
        Avg_Insp_Flow = Total_Insp_Flow / number_of_breaths
        avg_insp_flow_tbin.append(Avg_Insp_Flow)
        
        # Expiration flow average
        Total_Exp_Flow = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j])
            Total_Exp_Flow += time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_exp_flow_tbin_sem.append(x)
        Avg_Exp_Flow = Total_Exp_Flow / number_of_breaths
        avg_exp_flow_tbin.append(Avg_Exp_Flow)
    
    # Create the combined average data
    all_avg_vol_tbin = avg_insp_vol_tbin + avg_exp_vol_tbin
    all_avg_flow_tbin = avg_insp_flow_tbin + avg_exp_flow_tbin
    all_avg_vol_tbin_sem = avg_insp_vol_tbin_sem + avg_exp_vol_tbin_sem
    all_avg_flow_tbin_sem = avg_insp_flow_tbin_sem + avg_exp_flow_tbin_sem
    
    # Store insp and exp tidal volumes and times
    insp_exp_Vt_Tt = {
        'Inspiratory Tidal Volume': Vt_Insp_list,
        'Expiratory Tidal Volumes': Vt_Exp_list,
        'Inspiratory Total Time': Tt_Insp_list,
        'Expiratory Total Time': Tt_Exp_list
    }
    
    # Create a data dictionary with all results
    time_bins_result = {
        'time_bins_breath_dictionary': time_bins_breath_dictionary,
        'original_insp_data_breath_dictionary': original_insp_data_breath_dictionary,
        'original_exp_data_breath_dictionary': original_exp_data_breath_dictionary,
        'time_bin_copy': time_bin_copy,
        'Vt_Insp_list': Vt_Insp_list,
        'Vt_Exp_list': Vt_Exp_list,
        'Tt_Insp_list': Tt_Insp_list,
        'Tt_Exp_list': Tt_Exp_list,
        'avg_insp_vol_tbin': avg_insp_vol_tbin,
        'avg_exp_vol_tbin': avg_exp_vol_tbin,
        'avg_insp_flow_tbin': avg_insp_flow_tbin,
        'avg_exp_flow_tbin': avg_exp_flow_tbin,
        'avg_insp_vol_tbin_sem': avg_insp_vol_tbin_sem,
        'avg_exp_vol_tbin_sem': avg_exp_vol_tbin_sem,
        'avg_insp_flow_tbin_sem': avg_insp_flow_tbin_sem,
        'avg_exp_flow_tbin_sem': avg_exp_flow_tbin_sem,
        'all_avg_vol_tbin': all_avg_vol_tbin,
        'all_avg_flow_tbin': all_avg_flow_tbin,
        'all_avg_vol_tbin_sem': all_avg_vol_tbin_sem,
        'all_avg_flow_tbin_sem': all_avg_flow_tbin_sem,
        'insp_exp_Vt_Tt': insp_exp_Vt_Tt,
        'Avg_Insp_Vt': Avg_Insp_Vt,
        'Avg_Exp_Vt': Avg_Exp_Vt,
        'Mean_shift': Mean_shift
    }
    
    return time_bins_result