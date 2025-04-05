"""
Respiratory Data Processor
Core data processing module
"""

import os
from data.reader import read_excel_file
from data.writer import create_separate_file_output, create_horizontal_layout_output
from config import OUTPUT_HORIZONTAL

def process_files(selected_files, tlc_values, subject_ids, output_option, output_path):
    """
    Process multiple files and generate the output
    
    Parameters:
    selected_files - List of file paths to process
    tlc_values - Dictionary mapping file paths to TLC values
    subject_ids - Dictionary mapping file paths to subject IDs
    output_option - String representing the output option: 'horizontal_layout' or 'separate_files'
    output_path - String with output file path (for horizontal layout)
    
    Returns:
    Dictionary with results including successful_files, failed_files, and output_path
    """
    total_files = len(selected_files)
    successful_files = []
    failed_files = []
    
    # Dictionary to store processed data frames
    processed_dfs = {}
    all_insp_vols = []
    all_insp_flows = []
    all_exp_vols = []
    all_exp_flows = []
    max_rows = 0  # Track max rows for padding
    
    for file_path in selected_files:
        filename = os.path.basename(file_path)
        
        try:
            # Get the TLC value for this file
            tlc = tlc_values[file_path]
            
            # Get the Subject ID for this file (if available)
            subject_id = subject_ids.get(file_path, "")
            subject_suffix = f" {subject_id}" if subject_id else ""
            
            # Process the file
            insp_vol, insp_flow, exp_vol, exp_flow, n_rows, raw_insp_vol, raw_exp_vol, success = read_excel_file(file_path, tlc, subject_id)
            
            if success:
                successful_files.append(filename)
                
                # Store the data columns for this file
                processed_dfs[file_path] = {
                    'insp_vol': insp_vol,
                    'insp_flow': insp_flow,
                    'exp_vol': exp_vol,
                    'exp_flow': exp_flow,
                    'raw_insp_vol': raw_insp_vol,
                    'raw_exp_vol': raw_exp_vol,
                    'tlc': tlc,
                    'subject_id': subject_id,
                    'filename': filename
                }
                
                # Add to the lists for averaging
                all_insp_vols.append(insp_vol)
                all_insp_flows.append(insp_flow)
                all_exp_vols.append(exp_vol)
                all_exp_flows.append(exp_flow)
                
                # Update max rows if needed
                max_rows = max(max_rows, n_rows)
                
                # For separate files, create individual outputs
                if output_option != OUTPUT_HORIZONTAL:
                    create_separate_file_output(file_path, insp_vol, insp_flow, exp_vol, exp_flow, tlc, subject_suffix)
                    
            else:
                failed_files.append(filename)
        except Exception as e:
            failed_files.append(f"{filename} (Error: {str(e)})")
    
    # Create horizontal layout output if needed and have successful files
    if output_option == OUTPUT_HORIZONTAL and processed_dfs:
        create_horizontal_layout_output(selected_files, processed_dfs, all_insp_vols, all_insp_flows, 
                                       all_exp_vols, all_exp_flows, max_rows, output_path)
    
    # Prepare result
    result = {
        'successful_files': successful_files,
        'failed_files': failed_files,
        'output_path': output_path if output_option == OUTPUT_HORIZONTAL else ""
    }
    
    return result