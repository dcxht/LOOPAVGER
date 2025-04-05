"""
Respiratory Data Processor
Volume bins calculations module
"""

import pandas as pd
import numpy as np
from statistics import mean

def process_volume_bins(time_bins_result, intervals, number_of_breaths):
    """
    Process respiratory data using the volume bins method
    
    Parameters:
    time_bins_result - Dictionary with time bins results
    intervals - Number of intervals to divide each breath into
    number_of_breaths - Number of breaths to process
    
    Returns:
    Dictionary with volume bins data for each breath and average volume bins data
    """
    # Extract necessary data from time bins result
    original_insp_data_breath_dictionary = time_bins_result['original_insp_data_breath_dictionary']
    original_exp_data_breath_dictionary = time_bins_result['original_exp_data_breath_dictionary']
    Vt_Insp_list = time_bins_result['Vt_Insp_list']
    Vt_Exp_list = time_bins_result['Vt_Exp_list']
    
    # Initiate Dictionary for Volume Bins
    volume_bins_breath_dictionary = {}
    
    # Process each breath
    for i in range(number_of_breaths):
        # Create new breath dictionary
        Breath_Dict_Name = f"Breath_{i}"
        volume_bins_breath_dictionary[Breath_Dict_Name] = {}
        
        # Extract original data
        Insp_Time = original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Time"]
        insp_vol = original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Vol"]
        Insp_Flow = original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Flow"]
        Exp_Time = original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Time"]
        Exp_Volume = original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Vol"]
        Exp_Flow = original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Flow"]
        
        # Find incremental Inspiratory Volume values for volume bins
        insp_vol_intervals_vbins = []
        incr_insp_vol = Vt_Insp_list[i] / intervals
        Start_Insp_Value = insp_vol[0]
        
        for j in range(intervals + 1):
            Vt_insp_value = incr_insp_vol * j
            Vt_insp_value = Start_Insp_Value - Vt_insp_value
            insp_vol_intervals_vbins.append(Vt_insp_value)
        
        # Find incremental Expiratory Volume values for volume bins
        exp_vol_intervals_vbins = []
        incr_exp_vol = Vt_Exp_list[i] / intervals
        Start_Exp_Value = Exp_Volume[0]
        
        for j in range(intervals + 1):
            Vt_exp_value = incr_exp_vol * j
            Vt_exp_value = Start_Exp_Value + Vt_exp_value
            exp_vol_intervals_vbins.append(Vt_exp_value)
        
        # Interpolate values for Flow based on volume intervals
        insp_flow_intervals_vbins = []
        
        for j in range(len(insp_vol_intervals_vbins)):
            Actual_Volume_Interval = insp_vol_intervals_vbins[j]
            for l in range(len(insp_vol)):
                try:
                    if Actual_Volume_Interval == insp_vol[0]:
                        insp_flow_intervals_vbins.append(Insp_Flow[0])
                        break
                    elif insp_vol[l] == Actual_Volume_Interval:
                        insp_flow_intervals_vbins.append(Insp_Flow[l])
                        break
                    elif Actual_Volume_Interval == insp_vol[-1]:
                        insp_flow_intervals_vbins.append(Insp_Flow[-1])
                        break
                    elif insp_vol[l] > Actual_Volume_Interval > insp_vol[l + 1]:
                        t1 = Insp_Time[l]
                        t2 = Insp_Time[l + 1]
                        v1 = insp_vol[l]
                        v2 = insp_vol[l + 1]
                        f1 = Insp_Flow[l]
                        f2 = Insp_Flow[l + 1]
                        
                        Time_at_Volume_Interval = t1 + ((Actual_Volume_Interval - v1) / ((v2 - v1) / (t2 - t1)))
                        Flow_at_Volume_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Time_at_Volume_Interval - t1)
                        
                        insp_flow_intervals_vbins.append(Flow_at_Volume_Interval)
                        break
                except IndexError:
                    insp_flow_intervals_vbins.append(Insp_Flow[l])
        
        # Interpolate values for Flow based on expiratory volume intervals
        exp_flow_intervals_vbins = []
        
        for j in range(len(exp_vol_intervals_vbins)):
            Actual_Volume_Interval = exp_vol_intervals_vbins[j]
            for l in range(len(Exp_Volume)):
                try:
                    if Actual_Volume_Interval == Exp_Volume[0]:
                        exp_flow_intervals_vbins.append(Exp_Flow[0])
                        break
                    elif Exp_Volume[l] == Actual_Volume_Interval:
                        exp_flow_intervals_vbins.append(Exp_Flow[l])
                        break
                    elif Actual_Volume_Interval == Exp_Volume[-1]:
                        exp_flow_intervals_vbins.append(Exp_Flow[-1])
                        break
                    elif Exp_Volume[l] < Actual_Volume_Interval < Exp_Volume[l + 1]:
                        t1 = Exp_Time[l]
                        t2 = Exp_Time[l + 1]
                        v1 = Exp_Volume[l]
                        v2 = Exp_Volume[l + 1]
                        f1 = Exp_Flow[l]
                        f2 = Exp_Flow[l + 1]
                        
                        Time_at_Volume_Interval = t1 + ((Actual_Volume_Interval - v1) / ((v2 - v1) / (t2 - t1)))
                        Flow_at_Volume_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Time_at_Volume_Interval - t1)
                        
                        exp_flow_intervals_vbins.append(Flow_at_Volume_Interval)
                        break
                except IndexError:
                    exp_flow_intervals_vbins.append(Exp_Flow[l])
        
        # Store volume bins data
        volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"] = insp_vol_intervals_vbins
        volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"] = insp_flow_intervals_vbins
        volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"] = exp_vol_intervals_vbins
        volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"] = exp_flow_intervals_vbins
    
    # Calculate average volume bin data
    avg_insp_vol_vbin = []
    avg_exp_vol_vbin = []
    avg_insp_flow_vbin = []
    avg_exp_flow_vbin = []
    avg_insp_vol_vbin_sem = []
    avg_exp_vol_vbin_sem = []
    avg_insp_flow_vbin_sem = []
    avg_exp_flow_vbin_sem = []
    
    for j in range(intervals + 1):
        # Inspiration volume average
        Total_Insp_Volume = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j])
            Total_Insp_Volume += volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_insp_vol_vbin_sem.append(x)
        Avg_Insp_Vol = Total_Insp_Volume / number_of_breaths
        avg_insp_vol_vbin.append(Avg_Insp_Vol)
        
        # Expiration volume average
        Total_Exp_Volume = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j])
            Total_Exp_Volume += volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_exp_vol_vbin_sem.append(x)
        Avg_Exp_Vol = Total_Exp_Volume / number_of_breaths
        avg_exp_vol_vbin.append(Avg_Exp_Vol)
        
        # Inspiration flow average
        Total_Insp_Flow = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j])
            Total_Insp_Flow += volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_insp_flow_vbin_sem.append(x)
        Avg_Insp_Flow = Total_Insp_Flow / number_of_breaths
        avg_insp_flow_vbin.append(Avg_Insp_Flow)
        
        # Expiration flow average
        Total_Exp_Flow = 0
        temp_sem = []
        for i in range(number_of_breaths):
            temp_sem.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j])
            Total_Exp_Flow += volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j]
        temp_sem = np.array(temp_sem)
        x = np.std(temp_sem, ddof=1)
        avg_exp_flow_vbin_sem.append(x)
        Avg_Exp_Flow = Total_Exp_Flow / number_of_breaths
        avg_exp_flow_vbin.append(Avg_Exp_Flow)
    
    # Create combined average data
    all_avg_vbin_vol_list = avg_insp_vol_vbin + avg_exp_vol_vbin
    all_avg_vbin_flow_list = avg_insp_flow_vbin + avg_exp_flow_vbin
    all_avg_vol_vbin_sem = avg_insp_vol_vbin_sem + avg_exp_vol_vbin_sem
    all_avg_flow_vbin_sem = avg_insp_flow_vbin_sem + avg_exp_flow_vbin_sem
    
    # Create a volume bins data dictionary
    volume_bins_result = {
        'volume_bins_breath_dictionary': volume_bins_breath_dictionary,
        'avg_insp_vol_vbin': avg_insp_vol_vbin,
        'avg_exp_vol_vbin': avg_exp_vol_vbin,
        'avg_insp_flow_vbin': avg_insp_flow_vbin,
        'avg_exp_flow_vbin': avg_exp_flow_vbin,
        'avg_insp_vol_vbin_sem': avg_insp_vol_vbin_sem,
        'avg_exp_vol_vbin_sem': avg_exp_vol_vbin_sem,
        'avg_insp_flow_vbin_sem': avg_insp_flow_vbin_sem,
        'avg_exp_flow_vbin_sem': avg_exp_flow_vbin_sem,
        'all_avg_vbin_vol_list': all_avg_vbin_vol_list,
        'all_avg_vbin_flow_list': all_avg_vbin_flow_list,
        'all_avg_vol_vbin_sem': all_avg_vol_vbin_sem,
        'all_avg_flow_vbin_sem': all_avg_flow_vbin_sem
    }
    
    return volume_bins_result