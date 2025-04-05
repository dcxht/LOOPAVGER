"""
Respiratory Data Processor
Configuration settings and constants
"""

# Application settings
APP_TITLE = "RespiratoryDataProcessor"
APP_WIDTH = 600
APP_HEIGHT = 450

# File settings
DEFAULT_EXTENSION = ".xlsx"
EXCEL_FILETYPES = [("Excel files", "*.xlsx")]

# Column name patterns to search for in Excel files
VOL_INSP_PATTERN = ["insp", "vol"]
FLOW_INSP_PATTERN = ["insp", "flow"]
VOL_EXP_PATTERN = ["exp", "vol"]
FLOW_EXP_PATTERN = ["exp", "flow"]

# Default sheet name to look for in Excel files
DEFAULT_SHEET = "Avg Vol Bin Data"

# Output options
OUTPUT_HORIZONTAL = "horizontal_layout"
OUTPUT_SEPARATE = "separate_files"

# Default messages
DEFAULT_OUTPUT_MESSAGE = "Output will be saved in original file locations"