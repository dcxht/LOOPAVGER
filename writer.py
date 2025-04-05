"""
Respiratory Data Processor
Excel file writing functions
"""

import pandas as pd
import os
import numpy as np

def create_separate_file_output(file_path, insp_vol, insp_flow, exp_vol, exp_flow, tlc, subject_suffix):
    """
    Create a separate output file for a single input file
    
    Parameters:
    file_path - String path to the input file
    insp_vol - Series with inspiration volume data (% of TLC)
    insp_flow - Series with inspiration flow data
    exp_vol - Series with expiration volume data (% of TLC)
    exp_flow - Series with expiration flow data
    tlc - Float TLC value
    subject_suffix - String with subject ID to append to column names
    
    Returns:
    String path to the output file
    """
    # Create output file path
    output_path = file_path.replace('.xlsx', f'_TLC_percent{subject_suffix}.xlsx')
    
    # Create output dataframe
    output_df = pd.DataFrame({
        'Vol % TLC': pd.concat([insp_vol, exp_vol], ignore_index=True),
        f'Flow{subject_suffix}': pd.concat([insp_flow, exp_flow], ignore_index=True)
    })
    
    # Save to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write the main data
        output_df.to_excel(writer, sheet_name="Data", index=False)
        
        # Add TLC value at the bottom after skipping a row
        tlc_df = pd.DataFrame({
            "": ["", "TLC"],
            "Value": ["", tlc]
        })
        
        # Write the TLC information below the main data
        tlc_df.to_excel(writer, sheet_name="Data", startrow=len(output_df) + 2, index=False)
    
    return output_path

def create_horizontal_layout_output(selected_files, processed_dfs, all_insp_vols, all_insp_flows, 
                                   all_exp_vols, all_exp_flows, max_rows, output_path):
    """
    Create a consolidated output file with all data side by side and averages on a second sheet
    
    Parameters:
    selected_files - List of file paths
    processed_dfs - Dictionary mapping file paths to dictionaries of processed data
    all_insp_vols - List of Series with inspiration volume data
    all_insp_flows - List of Series with inspiration flow data
    all_exp_vols - List of Series with expiration volume data
    all_exp_flows - List of Series with expiration flow data
    max_rows - Integer with maximum number of rows across all files
    output_path - String path for the output file
    
    Returns:
    None
    """
    # Create a combined dataframe with all files side by side
    combined_data = {}
    raw_data = {}
    
    # Create a data frame to store TLC values
    tlc_summary = []
    all_tlc_values = []  # For calculating average TLC
    
    # Process each file to create side-by-side columns
    for i, file_path in enumerate(selected_files):
        if file_path in processed_dfs:
            file_data = processed_dfs[file_path]
            subject_id = file_data['subject_id']
            subject_suffix = f" {subject_id}" if subject_id else ""
            filename = os.path.splitext(file_data['filename'])[0]
            tlc_value = file_data['tlc']
            all_tlc_values.append(tlc_value)
            
            # Get inspiration data
            insp_vol = file_data['insp_vol']
            insp_flow = file_data['insp_flow']
            
            # Get expiration data
            exp_vol = file_data['exp_vol']
            exp_flow = file_data['exp_flow']
            
            # Get original (raw) data if available
            raw_insp_vol = file_data.get('raw_insp_vol', insp_vol)
            raw_exp_vol = file_data.get('raw_exp_vol', exp_vol)
            
            # Pad series to max_rows if needed
            if len(insp_vol) < max_rows:
                insp_vol = insp_vol.reindex(range(max_rows)).fillna("")
                insp_flow = insp_flow.reindex(range(max_rows)).fillna("")
                raw_insp_vol = raw_insp_vol.reindex(range(max_rows)).fillna("")
            
            if len(exp_vol) < max_rows:
                exp_vol = exp_vol.reindex(range(max_rows)).fillna("")
                exp_flow = exp_flow.reindex(range(max_rows)).fillna("")
                raw_exp_vol = raw_exp_vol.reindex(range(max_rows)).fillna("")
            
            # Add to combined data with subject ID in column name
            vol_col_name = f"Vol % TLC {subject_id}" if subject_id else f"Vol % TLC {i+1}"
            flow_col_name = f"Flow{subject_suffix}" if subject_id else f"Flow {i+1}"
            
            # Concatenate inspiration and expiration data for percent TLC
            combined_data[vol_col_name] = pd.concat([insp_vol, exp_vol], ignore_index=True)
            combined_data[flow_col_name] = pd.concat([insp_flow, exp_flow], ignore_index=True)
            
            # Add to raw data
            raw_vol_col_name = f"Raw Vol {subject_id}" if subject_id else f"Raw Vol {i+1}"
            raw_data[raw_vol_col_name] = pd.concat([raw_insp_vol, raw_exp_vol], ignore_index=True)
            raw_data[flow_col_name] = pd.concat([insp_flow, exp_flow], ignore_index=True)
            
            # Add to TLC summary
            tlc_summary.append({
                "File": filename,
                "Subject ID": subject_id,
                "TLC Value": tlc_value
            })
    
    # Calculate average TLC
    avg_tlc = sum(all_tlc_values) / len(all_tlc_values) if all_tlc_values else 0
    avg_tlc = round(avg_tlc, 2)  # Round to 2 decimal places
    
    # Create the combined dataframe
    combined_df = pd.DataFrame(combined_data)
    raw_df = pd.DataFrame(raw_data)
    
    # Create the averages dataframe
    avg_data = {}
    
    # Calculate average volume as % of TLC
    if all_insp_vols and all_exp_vols:
        # Pad all series to the same length for proper averaging
        padded_insp_vols = []
        for series in all_insp_vols:
            if len(series) < max_rows:
                padded_insp_vols.append(series.reindex(range(max_rows)).fillna(np.nan))
            else:
                padded_insp_vols.append(series)
        
        padded_exp_vols = []
        for series in all_exp_vols:
            if len(series) < max_rows:
                padded_exp_vols.append(series.reindex(range(max_rows)).fillna(np.nan))
            else:
                padded_exp_vols.append(series)
        
        # Calculate average inspiration and expiration volumes
        avg_insp_vol = pd.concat(padded_insp_vols, axis=1).mean(axis=1, skipna=True)
        avg_exp_vol = pd.concat(padded_exp_vols, axis=1).mean(axis=1, skipna=True)
        
        # Calculate average flow values
        padded_insp_flows = []
        for series in all_insp_flows:
            if len(series) < max_rows:
                padded_insp_flows.append(series.reindex(range(max_rows)).fillna(np.nan))
            else:
                padded_insp_flows.append(series)
        
        padded_exp_flows = []
        for series in all_exp_flows:
            if len(series) < max_rows:
                padded_exp_flows.append(series.reindex(range(max_rows)).fillna(np.nan))
            else:
                padded_exp_flows.append(series)
        
        avg_insp_flow = pd.concat(padded_insp_flows, axis=1).mean(axis=1, skipna=True)
        avg_exp_flow = pd.concat(padded_exp_flows, axis=1).mean(axis=1, skipna=True)
        
        # Create a dataframe with the averages
        avg_data['Average Vol % TLC'] = pd.concat([avg_insp_vol, avg_exp_vol], ignore_index=True)
        avg_data['Average Flow'] = pd.concat([avg_insp_flow, avg_exp_flow], ignore_index=True)
        
        # Create the averages dataframe
        avg_df = pd.DataFrame(avg_data)
    
    # Create absolute volume data (% of TLC converted back to absolute volume using average TLC)
    absolute_data = {}
    
    # For each column that contains Vol % TLC
    for col in combined_df.columns:
        if 'Vol % TLC' in col:
            # Create corresponding absolute volume column
            abs_col_name = col.replace('Vol % TLC', 'Absolute Vol')
            # Convert % TLC to absolute volume: (% * average TLC) / 100
            absolute_data[abs_col_name] = combined_df[col].apply(
                lambda x: (float(x) * avg_tlc / 100) if pd.notnull(x) and x != "" else x
            )
        elif 'Flow' in col:
            absolute_data[col] = combined_df[col]
    
    # Create the absolute volume dataframe
    absolute_df = pd.DataFrame(absolute_data)
    
    # Save to file
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write the raw data
        raw_df.to_excel(writer, sheet_name="Raw Data", index=False)
        
        # Write the main data (% of TLC)
        combined_df.to_excel(writer, sheet_name="Individual Data", index=False)
        
        # Add TLC summary at the bottom
        if tlc_summary:
            tlc_df = pd.DataFrame(tlc_summary)
            tlc_df.to_excel(writer, sheet_name="Individual Data", 
                           startrow=len(combined_df) + 3, index=False)
        
        # Add average TLC to the summary
        avg_tlc_df = pd.DataFrame({
            "": ["Average TLC"],
            "Value": [avg_tlc]
        })
        avg_tlc_df.to_excel(writer, sheet_name="Individual Data", 
                           startrow=len(combined_df) + len(tlc_summary) + 5, index=False)
        
        # Write the averages data to a separate sheet
        if 'avg_df' in locals():
            avg_df.to_excel(writer, sheet_name="Averages", index=False)
            
            # Add average TLC to the averages sheet
            avg_tlc_df = pd.DataFrame({
                "": ["", "Average TLC"],
                "Value": ["", avg_tlc]
            })
            avg_tlc_df.to_excel(writer, sheet_name="Averages", 
                             startrow=len(avg_df) + 2, index=False)
        
        # Write the absolute volume data (converted from % TLC)
        if 'absolute_df' in locals():
            absolute_df.to_excel(writer, sheet_name="Absolute Volume Data", index=False)
            
            # Add average TLC note to the absolute volume sheet
            avg_tlc_note_df = pd.DataFrame({
                "Note": [f"Absolute volumes calculated using average TLC: {avg_tlc}"]
            })
            avg_tlc_note_df.to_excel(writer, sheet_name="Absolute Volume Data", 
                                   startrow=len(absolute_df) + 2, index=False)
        
        # Write the normalized average data (converted from % TLC)
        if 'avg_df' in locals():
            # Create normalized average data
            normalized_avg_data = {}
            
            # Convert average % TLC to absolute volume
            if 'Average Vol % TLC' in avg_df.columns:
                normalized_avg_data['Normalized Average Volume'] = avg_df['Average Vol % TLC'].apply(
                    lambda x: (float(x) * avg_tlc / 100) if pd.notnull(x) and x != "" else x
                )
                
                # Keep the average flow as is
                normalized_avg_data['Average Flow'] = avg_df['Average Flow']
                
                # Add a blank column for spacing
                normalized_avg_data[''] = [""] * len(normalized_avg_data['Normalized Average Volume'])
                
                # Calculate standard deviation across all absolute volumes
                # First, get all absolute volume columns from the absolute_df
                vol_cols = [col for col in absolute_df.columns if 'Vol' in col]
                
                # For each row, calculate standard deviation across all subjects
                vol_std_dev = []
                for i in range(len(absolute_df)):
                    # Get all volume values for this row across subjects
                    row_values = []
                    for col in vol_cols:
                        value = absolute_df.iloc[i][col]
                        if pd.notnull(value) and value != "":
                            try:
                                row_values.append(float(value))
                            except (ValueError, TypeError):
                                pass
                    
                    # Calculate standard deviation if we have enough values
                    if len(row_values) > 1:
                        std = np.std(row_values, ddof=1)  # Using n-1 for sample std dev
                        vol_std_dev.append(round(std, 3))
                    else:
                        vol_std_dev.append(None)
                
                # Add volume standard deviation column with proper padding
                # Pad to match the length of normalized_avg_data
                if len(vol_std_dev) < len(normalized_avg_data['Normalized Average Volume']):
                    vol_std_dev.extend([None] * (len(normalized_avg_data['Normalized Average Volume']) - len(vol_std_dev)))
                normalized_avg_data['Volume StdDev'] = vol_std_dev
                
                # Calculate standard deviation across all flow values
                # First, get all flow columns from the absolute_df
                flow_cols = [col for col in absolute_df.columns if 'Flow' in col]
                
                # For each row, calculate standard deviation across all subjects
                flow_std_dev = []
                for i in range(len(absolute_df)):
                    # Get all flow values for this row across subjects
                    row_values = []
                    for col in flow_cols:
                        value = absolute_df.iloc[i][col]
                        if pd.notnull(value) and value != "":
                            try:
                                row_values.append(float(value))
                            except (ValueError, TypeError):
                                pass
                    
                    # Calculate standard deviation if we have enough values
                    if len(row_values) > 1:
                        std = np.std(row_values, ddof=1)  # Using n-1 for sample std dev
                        flow_std_dev.append(round(std, 3))
                    else:
                        flow_std_dev.append(None)
                
                # Add flow standard deviation column with proper padding
                # Pad to match the length of normalized_avg_data
                if len(flow_std_dev) < len(normalized_avg_data['Normalized Average Volume']):
                    flow_std_dev.extend([None] * (len(normalized_avg_data['Normalized Average Volume']) - len(flow_std_dev)))
                normalized_avg_data['Flow StdDev'] = flow_std_dev
                
                # Create the normalized averages dataframe
                normalized_avg_df = pd.DataFrame(normalized_avg_data)
                
                # Write to a new sheet
                normalized_avg_df.to_excel(writer, sheet_name="Normalized Average Data", index=False)
                
                # Add explanation note
                norm_note_df = pd.DataFrame({
                    "Note": [f"Normalized average volume calculated using average TLC: {avg_tlc}"]
                })
                norm_note_df.to_excel(writer, sheet_name="Normalized Average Data", 
                                     startrow=len(normalized_avg_df) + 2, index=False)
                
                # Add standard deviation explanation
                std_note_df = pd.DataFrame({
                    "Note": ["Volume StdDev: Standard deviation across all subjects' absolute volumes",
                           "Flow StdDev: Standard deviation across all subjects' flow values"]
                })
                std_note_df.to_excel(writer, sheet_name="Normalized Average Data", 
                                   startrow=len(normalized_avg_df) + 4, index=False)