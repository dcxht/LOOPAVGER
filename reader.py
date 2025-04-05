"""
Respiratory Data Processor
Excel file reading functions
"""

import pandas as pd
from utils.helpers import find_column
from config import (
    VOL_INSP_PATTERN, FLOW_INSP_PATTERN, 
    VOL_EXP_PATTERN, FLOW_EXP_PATTERN,
    DEFAULT_SHEET
)

def read_excel_file(file_path, tlc, subject_id):
    """
    Read and process data from an Excel file
    
    Parameters:
    file_path - String path to the Excel file
    tlc - Float TLC value for this file
    subject_id - String subject ID (can be empty)
    
    Returns:
    Tuple with processed data and success flag (insp_vol, insp_flow, exp_vol, exp_flow, n_rows, raw_insp_vol, raw_exp_vol, success)
    """
    try:
        # First, get all sheet names
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        
        # Check if target sheet exists
        if DEFAULT_SHEET in sheet_names:
            df = pd.read_excel(file_path, sheet_name=DEFAULT_SHEET)
        else:
            # If not, just read the first sheet
            df = pd.read_excel(file_path)
        
        # Find the required columns
        insp_vol_col = find_column(df, VOL_INSP_PATTERN)
        insp_flow_col = find_column(df, FLOW_INSP_PATTERN)
        exp_vol_col = find_column(df, VOL_EXP_PATTERN)
        exp_flow_col = find_column(df, FLOW_EXP_PATTERN)
        
        # Check if all columns were found
        if not all([insp_vol_col, insp_flow_col, exp_vol_col, exp_flow_col]):
            return None, None, None, None, 0, None, None, False
        
        # Store raw volume data
        raw_insp_vol = df[insp_vol_col].copy()
        raw_exp_vol = df[exp_vol_col].copy()
        
        # Calculate percentage of TLC for volume columns ONLY
        insp_vol_percent = (df[insp_vol_col] / tlc) * 100
        exp_vol_percent = (df[exp_vol_col] / tlc) * 100
        
        # Keep flow columns unchanged
        insp_flow = df[insp_flow_col]
        exp_flow = df[exp_flow_col]
        
        # Get the maximum number of rows
        n_rows = max(len(insp_vol_percent), len(exp_vol_percent))
        
        return insp_vol_percent, insp_flow, exp_vol_percent, exp_flow, n_rows, raw_insp_vol, raw_exp_vol, True
        
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return None, None, None, None, 0, None, None, False