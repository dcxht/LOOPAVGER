"""
Respiratory Data Processor
Flow-Volume Averaging (FVAvg) core functionality
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from openpyxl import Workbook
from statistics import mean

from analysis.time_bins import process_time_bins
from analysis.volume_bins import process_volume_bins
from analysis.plotting import (
    plot_individual_time_bins, plot_individual_volume_bins,
    plot_average_time_bins, plot_average_volume_bins,
    plot_comparison, plot_max_loop_comparison, plot_original_data
)
from utils.helpers import create_workbook

def find_zero_flow_points(time_raw_list, vol_raw_list, flow_raw_list):
    """
    Find zero flow points and interpolate volume and time values
    
    Parameters:
    time_raw_list - List of raw time values
    vol_raw_list - List of raw volume values
    flow_raw_list - List of raw flow values
    
    Returns:
    Tuple of (zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list)
    """
    # Initialize lists
    zeroed_time_list = []
    zeroed_vol_list = []
    zeroed_flow_list = []
    phase_indexes = 0
    phase_indexes_list = []
    
    # Process each data point
    for i in range(len(flow_raw_list)):
        try:
            # Check for negative to positive flow transition
            if flow_raw_list[i] < 0 < flow_raw_list[i + 1]:
                counter = 0
                for j in range(1, 31):  # Check next 30 values
                    if flow_raw_list[i + 1 + j] > 0:
                        counter = counter + 1
                back_track = 0
                for j in range(41, 61):  # Check previous values
                    try:
                        back_track = flow_raw_list[i - j] + back_track
                    except IndexError:
                        pass
                
                back_track = back_track / 20
                
                # Only interpolate if both checks pass
                if counter == 30 and back_track < 0:
                    # Append values before zero flow point
                    zeroed_time_list.append(time_raw_list[i])
                    zeroed_flow_list.append(flow_raw_list[i])
                    zeroed_vol_list.append(vol_raw_list[i])
                    
                    # Assign variables for interpolation
                    t1 = time_raw_list[i]
                    t2 = time_raw_list[i + 1]
                    v1 = vol_raw_list[i]
                    v2 = vol_raw_list[i + 1]
                    f1 = flow_raw_list[i]
                    f2 = flow_raw_list[i + 1]
                    
                    # Linear interpolation for time at zero flow
                    interpolated_time = t1 + ((0 - f1) / ((f2 - f1) / (t2 - t1)))
                    zeroed_time_list.append(interpolated_time)
                    zeroed_time_list.append(interpolated_time)
                    
                    # Guesstimated volume
                    min_vol = min(v1, v2)
                    interpolated_volume = min_vol - 0.001
                    zeroed_vol_list.append(interpolated_volume)
                    zeroed_vol_list.append(interpolated_volume)
                    
                    # Append zero flow values
                    zeroed_flow_list.append(0)
                    zeroed_flow_list.append(0)
                    
                    # Update phase indexes
                    phase_indexes = phase_indexes + 2
                    phase_indexes_list.append(phase_indexes)
                    phase_indexes = 1
                else:
                    # Standard procedure if checks fail
                    zeroed_time_list.append(time_raw_list[i])
                    zeroed_flow_list.append(flow_raw_list[i])
                    zeroed_vol_list.append(vol_raw_list[i])
                    phase_indexes = phase_indexes + 1
                    
            # Check for positive to negative flow transition
            elif flow_raw_list[i] > 0 > flow_raw_list[i + 1]:
                counter = 0
                for j in range(1, 31):  # Check next 30 values
                    if flow_raw_list[i + 1 + j] < 0:
                        counter = counter + 1
                back_track = 0
                for j in range(41, 61):  # Check previous values
                    try:
                        back_track = flow_raw_list[i - j] + back_track
                    except IndexError:
                        pass
                
                back_track = back_track / 20
                
                # Only interpolate if both checks pass
                if counter == 30 and back_track > 0:
                    # Append values before zero flow point
                    zeroed_time_list.append(time_raw_list[i])
                    zeroed_flow_list.append(flow_raw_list[i])
                    zeroed_vol_list.append(vol_raw_list[i])
                    
                    # Assign variables for interpolation
                    t1 = time_raw_list[i]
                    t2 = time_raw_list[i + 1]
                    v1 = vol_raw_list[i]
                    v2 = vol_raw_list[i + 1]
                    f1 = flow_raw_list[i]
                    f2 = flow_raw_list[i + 1]
                    
                    # Linear interpolation for time at zero flow
                    interpolated_time = t1 + ((0 - f1) / ((f2 - f1) / (t2 - t1)))
                    zeroed_time_list.append(interpolated_time)
                    zeroed_time_list.append(interpolated_time)
                    
                    # Guesstimated volume
                    max_vol = max(v1, v2)
                    interpolated_volume = max_vol + 0.001
                    zeroed_vol_list.append(interpolated_volume)
                    zeroed_vol_list.append(interpolated_volume)
                    
                    # Append zero flow values
                    zeroed_flow_list.append(0)
                    zeroed_flow_list.append(0)
                    
                    # Update phase indexes
                    phase_indexes = phase_indexes + 2
                    phase_indexes_list.append(phase_indexes)
                    phase_indexes = 1
                else:
                    # Standard procedure if checks fail
                    zeroed_time_list.append(time_raw_list[i])
                    zeroed_flow_list.append(flow_raw_list[i])
                    zeroed_vol_list.append(vol_raw_list[i])
                    phase_indexes = phase_indexes + 1
            else:
                # Standard procedure for consecutive values with same sign
                zeroed_time_list.append(time_raw_list[i])
                zeroed_flow_list.append(flow_raw_list[i])
                zeroed_vol_list.append(vol_raw_list[i])
                phase_indexes = phase_indexes + 1
                
        except IndexError:
            # Handle the last data point
            zeroed_time_list.append(time_raw_list[-1])
            zeroed_flow_list.append(flow_raw_list[-1])
            zeroed_vol_list.append(vol_raw_list[-1])
            phase_indexes = phase_indexes + 1
    
    return zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list

def delete_row(index, zeroed_flow_list, zeroed_vol_list, zeroed_time_list):
    """
    Delete a row from all three lists at the given index
    
    Parameters:
    index - Index to delete
    zeroed_flow_list - List of flow values
    zeroed_vol_list - List of volume values
    zeroed_time_list - List of time values
    
    Returns:
    None (modifies the input lists in-place)
    """
    del zeroed_flow_list[index]
    del zeroed_vol_list[index]
    del zeroed_time_list[index]

def trim_excess_data(zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list):
    """
    Trim excess data to get complete breaths only
    
    Parameters:
    zeroed_time_list - List of zeroed time values
    zeroed_vol_list - List of zeroed volume values
    zeroed_flow_list - List of zeroed flow values
    phase_indexes_list - List of phase indexes
    
    Returns:
    Tuple of (zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list, number_of_breaths)
    """
    # Trim beginning
    counter_start = 1  # Will always delete the first phase index
    while True:
        if zeroed_flow_list[0] == 0 and zeroed_flow_list[2] < 0:
            delete_row(0, zeroed_flow_list, zeroed_vol_list, zeroed_time_list)
            break
        else:
            if zeroed_flow_list[0] == 0 and zeroed_flow_list[2] > 0:
                counter_start = counter_start + 0.5
            delete_row(0, zeroed_flow_list, zeroed_vol_list, zeroed_time_list)
    
    # Trim end
    counter_end = 0
    while True:
        if zeroed_flow_list[-3] == 0 and zeroed_flow_list[-1] < 0:
            delete_row(-1, zeroed_flow_list, zeroed_vol_list, zeroed_time_list)
            delete_row(-1, zeroed_flow_list, zeroed_vol_list, zeroed_time_list)
            delete_row(-1, zeroed_flow_list, zeroed_vol_list, zeroed_time_list)
            break
        else:
            if zeroed_flow_list[-3] == 0 and zeroed_flow_list[-1] > 0:
                counter_end = counter_end + 0.5
            delete_row(-1, zeroed_flow_list, zeroed_vol_list, zeroed_time_list)
    
    # Adjust phase indexes based on counters
    if counter_start == 1:
        del phase_indexes_list[0]
    elif counter_start == 2:
        del phase_indexes_list[0]
        del phase_indexes_list[0]
    
    if counter_end == 1:
        del phase_indexes_list[-1]
    
    # Calculate number of breaths
    number_of_breaths = int(len(phase_indexes_list) / 2)
    
    return zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list, number_of_breaths

def process_fvavg(file_path, intervals=100, output_filename=None):
    """
    Process a flow-volume file using the FVAvg algorithm
    
    Parameters:
    file_path - Path to the input Excel file
    intervals - Number of intervals to divide each breath into (default: 100)
    output_filename - Path to the output Excel file (default: based on input file)
    
    Returns:
    Dictionary with processing results
    """
    # Set default output filename if not provided
    if output_filename is None:
        output_filename = os.path.splitext(file_path)[0] + "_processed.xlsx"
    
    # Create the output workbook
    create_workbook(output_filename)
    
    # Read raw data from Excel
    raw_data = pd.read_excel(file_path, usecols=['Time', 'Vol', 'Flow'])
    time_raw_list = raw_data['Time'].tolist()
    vol_raw_list = raw_data['Vol'].tolist()
    flow_raw_list = raw_data['Flow'].tolist()
    
    # Find zero flow points
    zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list = find_zero_flow_points(
        time_raw_list, vol_raw_list, flow_raw_list
    )
    
    # Convert to DataFrame and save to Excel
    zeroed_raw_dict = {
        'Time': zeroed_time_list,
        'Vol': zeroed_vol_list,
        'Flow': zeroed_flow_list
    }
    zeroed_raw_df = pd.DataFrame(zeroed_raw_dict)
    with pd.ExcelWriter(output_filename, mode='a') as writer:
        zeroed_raw_df.to_excel(writer, sheet_name='Zeroed_Raw_Data')
    
    # Trim excess data to get complete breaths
    zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list, number_of_breaths = trim_excess_data(
        zeroed_time_list, zeroed_vol_list, zeroed_flow_list, phase_indexes_list
    )
    
    # Process using time bins method
    time_bins_result = process_time_bins(
        zeroed_time_list.copy(),  # Deep copy to avoid modifying the original
        zeroed_vol_list.copy(),
        zeroed_flow_list.copy(),
        phase_indexes_list.copy(),
        intervals,
        number_of_breaths
    )
    
    # Process using volume bins method
    volume_bins_result = process_volume_bins(
        time_bins_result,
        intervals,
        number_of_breaths
    )
    
    # Save time bin data (not normalized)
    for i in range(number_of_breaths):
        sheet_name = f"Not Normalized Time Bin Breath {i}"
        df = pd.DataFrame(time_bins_result['time_bin_copy'][f"Breath_{i}"])
        with pd.ExcelWriter(output_filename, mode='a') as writer:
            df.to_excel(writer, sheet_name=sheet_name)
    
    # Save time bin data (normalized)
    for i in range(number_of_breaths):
        sheet_name = f"Normalized Time Bin Breath {i}"
        df = pd.DataFrame(time_bins_result['time_bins_breath_dictionary'][f"Breath_{i}"])
        with pd.ExcelWriter(output_filename, mode='a') as writer:
            df.to_excel(writer, sheet_name=sheet_name)
    
    # Save volume bin data
    for i in range(number_of_breaths):
        sheet_name = f"Volume Bin Breath {i}"
        df = pd.DataFrame(volume_bins_result['volume_bins_breath_dictionary'][f"Breath_{i}"])
        with pd.ExcelWriter(output_filename, mode='a') as writer:
            df.to_excel(writer, sheet_name=sheet_name)
    
    # Save original breath data
    for i in range(number_of_breaths):
        sheet_name = f"Original Breath {i}"
        df1 = pd.DataFrame(time_bins_result['original_insp_data_breath_dictionary'][f"Breath_{i}"])
        df2 = pd.DataFrame(time_bins_result['original_exp_data_breath_dictionary'][f"Breath_{i}"])
        df3 = pd.concat([df1, df2])
        with pd.ExcelWriter(output_filename, mode='a') as writer:
            df3.to_excel(writer, sheet_name=sheet_name)
    
    # Create and save comparison data for time bins
    insp_vol_dict = {}
    exp_vol_dict = {}
    insp_flow_dict = {}
    exp_flow_dict = {}
    
    # Create blank list for spacing
    blank_list = [" "] * (intervals + 1)
    
    # Populate comparison dictionaries for time bins
    for i in range(number_of_breaths):
        insp_vol_dict[f"InspVol_{i}"] = time_bins_result['time_bin_copy'][f"Breath_{i}"]["Insp_Vol"]
        exp_vol_dict[f"ExpVol_{i}"] = time_bins_result['time_bin_copy'][f"Breath_{i}"]["Exp_Vol"]
        insp_flow_dict[f"InspFlow_{i}"] = time_bins_result['time_bin_copy'][f"Breath_{i}"]["Insp_Flow"]
        exp_flow_dict[f"ExpFlow_{i}"] = time_bins_result['time_bin_copy'][f"Breath_{i}"]["Exp_Flow"]
    
    # Add averages and standard errors to comparison dictionaries
    insp_vol_dict["Avg_Insp_Vol"] = time_bins_result['avg_insp_vol_tbin']
    insp_vol_dict["SEM(aivt)"] = time_bins_result['avg_insp_vol_tbin_sem']
    insp_vol_dict["a"] = blank_list
    
    exp_vol_dict["Avg_Exp_Vol}"] = time_bins_result['avg_exp_vol_tbin']
    exp_vol_dict["SEM(aevt)"] = time_bins_result['avg_exp_vol_tbin_sem']
    exp_vol_dict["b"] = blank_list
    
    insp_flow_dict["Avg_Insp_Flow"] = time_bins_result['avg_insp_flow_tbin']
    insp_flow_dict["SEM(aift)"] = time_bins_result['avg_insp_flow_tbin_sem']
    insp_flow_dict["c "] = blank_list
    
    exp_flow_dict["Avg_Exp_Flow"] = time_bins_result['avg_exp_flow_tbin']
    exp_flow_dict["SEM(aeft)"] = time_bins_result['avg_exp_flow_tbin_sem']
    
    # Convert to DataFrames
    df_ivdt = pd.DataFrame(insp_vol_dict)
    df_evdt = pd.DataFrame(exp_vol_dict)
    df_ifdt = pd.DataFrame(insp_flow_dict)
    df_efdt = pd.DataFrame(exp_flow_dict)
    
    # Combine and save
    df_combined_tbin = pd.concat([df_ivdt, df_evdt, df_ifdt, df_efdt])
    with pd.ExcelWriter(output_filename, mode='a') as writer:
        df_combined_tbin.to_excel(writer, sheet_name="Comparison_Purposes_tbin")
    
    # Create and save comparison data for volume bins
    insp_vol_dict_vbin = {}
    exp_vol_dict_vbin = {}
    insp_flow_dict_vbin = {}
    exp_flow_dict_vbin = {}
    
    # Populate comparison dictionaries for volume bins
    for i in range(number_of_breaths):
        insp_vol_dict_vbin[f"InspVol_{i}"] = volume_bins_result['volume_bins_breath_dictionary'][f"Breath_{i}"]["Insp_Vol"]
        exp_vol_dict_vbin[f"ExpVol_{i}"] = volume_bins_result['volume_bins_breath_dictionary'][f"Breath_{i}"]["Exp_Vol"]
        insp_flow_dict_vbin[f"InspFlow_{i}"] = volume_bins_result['volume_bins_breath_dictionary'][f"Breath_{i}"]["Insp_Flow"]
        exp_flow_dict_vbin[f"ExpFlow_{i}"] = volume_bins_result['volume_bins_breath_dictionary'][f"Breath_{i}"]["Exp_Flow"]
    
    # Add averages and standard errors to comparison dictionaries
    insp_vol_dict_vbin["Avg_Insp_Vol"] = volume_bins_result['avg_insp_vol_vbin']
    insp_vol_dict_vbin["SEM(aivt)"] = volume_bins_result['avg_insp_vol_vbin_sem']
    insp_vol_dict_vbin["a"] = blank_list
    
    exp_vol_dict_vbin["Avg_Exp_Vol}"] = volume_bins_result['avg_exp_vol_vbin']
    exp_vol_dict_vbin["SEM(aevt)"] = volume_bins_result['avg_exp_vol_vbin_sem']
    exp_vol_dict_vbin["b"] = blank_list
    
    insp_flow_dict_vbin["Avg_Insp_Flow"] = volume_bins_result['avg_insp_flow_vbin']
    insp_flow_dict_vbin["SEM(aift)"] = volume_bins_result['avg_insp_flow_vbin_sem']
    insp_flow_dict_vbin["c "] = blank_list
    
    exp_flow_dict_vbin["Avg_Exp_Flow"] = volume_bins_result['avg_exp_flow_vbin']
    exp_flow_dict_vbin["SEM(aeft)"] = volume_bins_result['avg_exp_flow_vbin_sem']
    
    # Convert to DataFrames
    df_ivdv = pd.DataFrame(insp_vol_dict_vbin)
    df_evdv = pd.DataFrame(exp_vol_dict_vbin)
    df_ifdv = pd.DataFrame(insp_flow_dict_vbin)
    df_efdv = pd.DataFrame(exp_flow_dict_vbin)
    
    # Combine and save
    df_combined_vbin = pd.concat([df_ivdv, df_evdv, df_ifdv, df_efdv])
    with pd.ExcelWriter(output_filename, mode='a') as writer:
        df_combined_vbin.to_excel(writer, sheet_name="Comparison_Purposes_vbin")
    
    # Save insp and exp tidal volume and time info
    df_insp_exp_vt_tt = pd.DataFrame(time_bins_result['insp_exp_Vt_Tt'])
    with pd.ExcelWriter(output_filename, mode='a') as writer:
        df_insp_exp_vt_tt.to_excel(writer, sheet_name="Tidal Volume and Time Data")
    
    # Save average data
    avg_breaths_dictionary_tbin = {
        'Avg_Insp_Vol_Graph': time_bins_result['avg_insp_vol_tbin'],
        'Avg_Insp_Flow_Graph': time_bins_result['avg_insp_flow_tbin'],
        'Avg_Exp_Vol_Graph': time_bins_result['avg_exp_vol_tbin'],
        'Avg_Exp_Flow_Graph': time_bins_result['avg_exp_flow_tbin']
    }
    df_avg_breath_tbin = pd.DataFrame(avg_breaths_dictionary_tbin)
    with pd.ExcelWriter(output_filename, mode='a') as writer:
        df_avg_breath_tbin.to_excel(writer, sheet_name="Avg Time Bin Data")
    
    avg_breaths_dictionary_vbin = {
        'Avg_Insp_Vol_Graph': volume_bins_result['avg_insp_vol_vbin'],
        'Avg_Insp_Flow_Graph': volume_bins_result['avg_insp_flow_vbin'],
        'Avg_Exp_Vol_Graph': volume_bins_result['avg_exp_vol_vbin'],
        'Avg_Exp_Flow_Graph': volume_bins_result['avg_exp_flow_vbin']
    }
    df_avg_volume_bin_breath = pd.DataFrame(avg_breaths_dictionary_vbin)
    with pd.ExcelWriter(output_filename, mode='a') as writer:
        df_avg_volume_bin_breath.to_excel(writer, sheet_name="Avg Vol Bin Data")
    
    # Create a results dictionary
    results = {
        'output_filename': output_filename,
        'number_of_breaths': number_of_breaths,
        'intervals': intervals,
        'time_bins_result': time_bins_result,
        'volume_bins_result': volume_bins_result
    }
    
    return results

def process_max_loop(fvavg_results, max_loop_file_path):
    """
    Process a max loop file and compare with FVAvg results
    
    Parameters:
    fvavg_results - Dictionary with FVAvg processing results
    max_loop_file_path - Path to the max loop Excel file
    
    Returns:
    Figure object with the comparison plot
    """
    # Read max loop data
    max_loop_data = pd.read_excel(max_loop_file_path, usecols=['Vol', 'Flow'])
    max_loop_vol = max_loop_data['Vol'].tolist()
    max_loop_flow = max_loop_data['Flow'].tolist()
    
    # Get necessary data from fvavg results
    time_bins_result = fvavg_results['time_bins_result']
    volume_bins_result = fvavg_results['volume_bins_result']
    
    # Create comparison plot
    fig = plot_max_loop_comparison(
        time_bins_result,
        volume_bins_result,
        max_loop_vol,
        max_loop_flow
    )
    
    return fig

def generate_plots(fvavg_results, output_dir=None):
    """
    Generate and save plots from FVAvg results
    
    Parameters:
    fvavg_results - Dictionary with FVAvg processing results
    output_dir - Directory to save the plots (default: same as output file)
    
    Returns:
    List of saved plot filenames
    """
    # Extract results
    time_bins_result = fvavg_results['time_bins_result']
    volume_bins_result = fvavg_results['volume_bins_result']
    intervals = fvavg_results['intervals']
    number_of_breaths = fvavg_results['number_of_breaths']
    output_filename = fvavg_results['output_filename']
    
    # Set default output directory if not provided
    if output_dir is None:
        output_dir = os.path.dirname(output_filename)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate base filename
    base_filename = os.path.splitext(os.path.basename(output_filename))[0]
    
    # Create and save plots
    plot_files = []
    
    # Individual time bins (not normalized)
    fig1 = plot_individual_time_bins(time_bins_result, intervals, number_of_breaths, normalized=False)
    plot_file1 = os.path.join(output_dir, f"{base_filename}_time_bins_not_normalized.png")
    fig1.savefig(plot_file1)
    plt.close(fig1)
    plot_files.append(plot_file1)
    
    # Individual time bins (normalized)
    fig2 = plot_individual_time_bins(time_bins_result, intervals, number_of_breaths, normalized=True)
    plot_file2 = os.path.join(output_dir, f"{base_filename}_time_bins_normalized.png")
    fig2.savefig(plot_file2)
    plt.close(fig2)
    plot_files.append(plot_file2)
    
    # Individual volume bins
    fig3 = plot_individual_volume_bins(volume_bins_result, intervals, number_of_breaths)
    plot_file3 = os.path.join(output_dir, f"{base_filename}_volume_bins.png")
    fig3.savefig(plot_file3)
    plt.close(fig3)
    plot_files.append(plot_file3)
    
    # Average time bins
    fig4 = plot_average_time_bins(time_bins_result)
    plot_file4 = os.path.join(output_dir, f"{base_filename}_avg_time_bins.png")
    fig4.savefig(plot_file4)
    plt.close(fig4)
    plot_files.append(plot_file4)
    
    # Average volume bins
    fig5 = plot_average_volume_bins(volume_bins_result)
    plot_file5 = os.path.join(output_dir, f"{base_filename}_avg_volume_bins.png")
    fig5.savefig(plot_file5)
    plt.close(fig5)
    plot_files.append(plot_file5)
    
    # Comparison of time and volume bins
    fig6 = plot_comparison(time_bins_result, volume_bins_result)
    plot_file6 = os.path.join(output_dir, f"{base_filename}_comparison.png")
    fig6.savefig(plot_file6)
    plt.close(fig6)
    plot_files.append(plot_file6)
    
    # Original data with averages
    fig7 = plot_original_data(time_bins_result, volume_bins_result, number_of_breaths, intervals)
    plot_file7 = os.path.join(output_dir, f"{base_filename}_original_data.png")
    fig7.savefig(plot_file7)
    plt.close(fig7)
    plot_files.append(plot_file7)
    
    return plot_files