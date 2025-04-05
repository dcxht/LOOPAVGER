"""
Respiratory Data Processor
Plotting functions for visualization
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_individual_time_bins(time_bins_result, intervals, number_of_breaths, normalized=False):
    """
    Plot individual breaths using time bins method
    
    Parameters:
    time_bins_result - Dictionary with time bins results
    intervals - Number of intervals
    number_of_breaths - Number of breaths
    normalized - Whether to use normalized data (True) or not normalized data (False)
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    time_bins_breath_dictionary = time_bins_result['time_bins_breath_dictionary']
    
    # Plot each breath
    for i in range(number_of_breaths):
        # Initiate Lists for each breath
        indiv_vol_tbin = []
        indiv_flow_tbin = []
        
        # First append all inspiration data
        for j in range(intervals + 1):
            indiv_vol_tbin.append(time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j])
            indiv_flow_tbin.append(time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j])
        
        # Second append all expiration data
        for j in range(intervals + 1):
            indiv_vol_tbin.append(time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j])
            indiv_flow_tbin.append(time_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j])
        
        # Plot the data
        plt.plot(indiv_vol_tbin, indiv_flow_tbin, label=f"Breath_{i}")
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    title_suffix = "Normalized" if normalized else "Not Normalized"
    plt.title(f'Individual Breaths (Time Bins {title_suffix})')
    plt.legend()
    
    return fig

def plot_individual_volume_bins(volume_bins_result, intervals, number_of_breaths):
    """
    Plot individual breaths using volume bins method
    
    Parameters:
    volume_bins_result - Dictionary with volume bins results
    intervals - Number of intervals
    number_of_breaths - Number of breaths
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    volume_bins_breath_dictionary = volume_bins_result['volume_bins_breath_dictionary']
    
    # Plot each breath
    for i in range(number_of_breaths):
        # Initiate Lists for each breath
        indiv_vol_vbin = []
        indiv_flow_vbin = []
        
        # First append all inspiration data
        for j in range(intervals + 1):
            indiv_vol_vbin.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j])
            indiv_flow_vbin.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j])
        
        # Second append all expiration data
        for j in range(intervals + 1):
            indiv_vol_vbin.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j])
            indiv_flow_vbin.append(volume_bins_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j])
        
        # Plot the data
        plt.plot(indiv_vol_vbin, indiv_flow_vbin, label=f"Breath_{i}")
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    plt.title('Individual Breaths (Volume Bins)')
    plt.legend()
    
    return fig

def plot_average_time_bins(time_bins_result):
    """
    Plot average flow-volume loop using time bins method
    
    Parameters:
    time_bins_result - Dictionary with time bins results
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    all_avg_vol_tbin = time_bins_result['all_avg_vol_tbin']
    all_avg_flow_tbin = time_bins_result['all_avg_flow_tbin']
    all_avg_vol_tbin_sem = time_bins_result['all_avg_vol_tbin_sem']
    all_avg_flow_tbin_sem = time_bins_result['all_avg_flow_tbin_sem']
    
    # Plot the data with error bars
    plt.scatter(all_avg_vol_tbin, all_avg_flow_tbin)
    plt.errorbar(all_avg_vol_tbin, all_avg_flow_tbin, 
                yerr=all_avg_flow_tbin_sem,
                xerr=all_avg_vol_tbin_sem,
                fmt='o')
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    plt.title('Avg Flow Volume Loop (Time Bins)')
    
    return fig

def plot_average_volume_bins(volume_bins_result):
    """
    Plot average flow-volume loop using volume bins method
    
    Parameters:
    volume_bins_result - Dictionary with volume bins results
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    all_avg_vbin_vol_list = volume_bins_result['all_avg_vbin_vol_list']
    all_avg_vbin_flow_list = volume_bins_result['all_avg_vbin_flow_list']
    all_avg_vol_vbin_sem = volume_bins_result['all_avg_vol_vbin_sem']
    all_avg_flow_vbin_sem = volume_bins_result['all_avg_flow_vbin_sem']
    
    # Plot the data with error bars
    plt.scatter(all_avg_vbin_vol_list, all_avg_vbin_flow_list)
    plt.errorbar(all_avg_vbin_vol_list, all_avg_vbin_flow_list, 
                yerr=all_avg_flow_vbin_sem,
                xerr=all_avg_vol_vbin_sem,
                fmt='o')
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    plt.title('Avg Flow Volume Loop (Volume Bins)')
    
    return fig

def plot_comparison(time_bins_result, volume_bins_result):
    """
    Plot comparison of time bins and volume bins methods
    
    Parameters:
    time_bins_result - Dictionary with time bins results
    volume_bins_result - Dictionary with volume bins results
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    all_avg_vol_tbin = time_bins_result['all_avg_vol_tbin']
    all_avg_flow_tbin = time_bins_result['all_avg_flow_tbin']
    all_avg_vbin_vol_list = volume_bins_result['all_avg_vbin_vol_list']
    all_avg_vbin_flow_list = volume_bins_result['all_avg_vbin_flow_list']
    
    # Plot the data
    plt.plot(all_avg_vol_tbin, all_avg_flow_tbin, label="Time Bins")
    plt.plot(all_avg_vbin_vol_list, all_avg_vbin_flow_list, label="Vol Bins")
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    plt.title('Avg Flow Volume Loop (Time & Vol Bins)')
    plt.legend()
    
    return fig

def plot_max_loop_comparison(time_bins_result, volume_bins_result, max_loop_vol, max_loop_flow):
    """
    Plot comparison with max loop data
    
    Parameters:
    time_bins_result - Dictionary with time bins results
    volume_bins_result - Dictionary with volume bins results
    max_loop_vol - List of volume values for max loop
    max_loop_flow - List of flow values for max loop
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    all_avg_vol_tbin = time_bins_result['all_avg_vol_tbin']
    all_avg_flow_tbin = time_bins_result['all_avg_flow_tbin']
    all_avg_vbin_vol_list = volume_bins_result['all_avg_vbin_vol_list']
    all_avg_vbin_flow_list = volume_bins_result['all_avg_vbin_flow_list']
    
    # Plot the data
    plt.plot(max_loop_vol, max_loop_flow, label="Max Loop", linewidth=1.0)
    plt.plot(all_avg_vol_tbin, all_avg_flow_tbin, label="Time Bins", linewidth=3.0)
    plt.plot(all_avg_vbin_vol_list, all_avg_vbin_flow_list, label="Vol Bins", linewidth=3.0)
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    plt.title('Avg Flow Volume Loop with Max Loop')
    plt.legend()
    
    return fig

def plot_original_data(time_bins_result, volume_bins_result, number_of_breaths, intervals):
    """
    Plot original data with averages
    
    Parameters:
    time_bins_result - Dictionary with time bins results
    volume_bins_result - Dictionary with volume bins results
    number_of_breaths - Number of breaths
    intervals - Number of intervals
    
    Returns:
    Matplotlib figure object
    """
    fig = plt.figure(figsize=(10, 6))
    
    original_insp_data_breath_dictionary = time_bins_result['original_insp_data_breath_dictionary']
    original_exp_data_breath_dictionary = time_bins_result['original_exp_data_breath_dictionary']
    all_avg_vol_tbin = time_bins_result['all_avg_vol_tbin']
    all_avg_flow_tbin = time_bins_result['all_avg_flow_tbin']
    all_avg_vbin_vol_list = volume_bins_result['all_avg_vbin_vol_list']
    all_avg_vbin_flow_list = volume_bins_result['all_avg_vbin_flow_list']
    
    # Plot each breath
    for i in range(number_of_breaths):
        original_volume = []
        original_flow = []
        
        # First append all inspiration data
        for j in range(len(original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Time"])):
            original_volume.append(original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j])
            original_flow.append(original_insp_data_breath_dictionary[f"Breath_{i}"]["Insp_Flow"][j])
        
        # Second append all expiration data
        for j in range(len(original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Time"])):
            original_volume.append(original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Vol"][j])
            original_flow.append(original_exp_data_breath_dictionary[f"Breath_{i}"]["Exp_Flow"][j])
        
        # Plot the data
        plt.plot(original_volume, original_flow, label=f"Breath_{i}")
    
    # Plot average curves
    plt.plot(all_avg_vbin_vol_list, all_avg_vbin_flow_list, label="Vol Bins", linewidth=3.0)
    plt.plot(all_avg_vol_tbin, all_avg_flow_tbin, label="Time Bins", linewidth=3.0)
    
    # Set labels and title
    plt.xlabel('Volume')
    plt.ylabel('Flow')
    plt.title('Original Individual Breaths with Averages')
    plt.legend()
    
    return fig