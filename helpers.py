"""
Helper functions for the Respiratory Data Processor
"""

import os
import pandas as pd
import re

def find_column(df, patterns):
    """
    Find a column in a DataFrame that contains all the given patterns
    
    Parameters:
    df - Pandas DataFrame to search
    patterns - List of strings to look for in column names
    
    Returns:
    Column name if found, None otherwise
    """
    patterns = [p.lower() for p in patterns]
    for col in df.columns:
        col_lower = str(col).lower()
        if all(p in col_lower for p in patterns):
            return col
    return None

def create_workbook(path):
    """
    Create a new Excel workbook at the given path
    
    Parameters:
    path - String path to create the workbook
    """
    from openpyxl import Workbook
    workbook = Workbook()
    workbook.save(path)

def get_basename(file_path):
    """
    Get the base filename without extension
    
    Parameters:
    file_path - String file path
    
    Returns:
    String with just the filename (no path or extension)
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def get_file_extension(file_path):
    """
    Get the file extension
    
    Parameters:
    file_path - String file path
    
    Returns:
    String with just the file extension
    """
    return os.path.splitext(file_path)[1]

def extract_subject_id(filename):
    """
    Extract a number between 2-7 digits from the filename to use as subject ID
    
    Parameters:
    filename - String containing the filename (can be full path or just basename)
    
    Returns:
    String with extracted subject ID or empty string if no ID could be extracted
    """
    # Get just the basename without extension
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Find the first occurrence of a 2-7 digit number in the filename
    match = re.search(r'\b\d{2,7}\b', base_name)
    
    # If found, return it as the subject ID
    if match:
        return match.group(0)
    
    return ""