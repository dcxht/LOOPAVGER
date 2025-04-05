#!/usr/bin/env python3
"""
Respiratory Data Processor
Main application entry point

This module initializes the application and starts the GUI.
The application provides three tools for respiratory data analysis:
1. Data Formatter - Converts raw respiratory data files to the proper format
2. Flow-Volume Averaging (FVAvg) - Performs advanced breath-by-breath analysis
3. Data Processor - Converts volume to % of TLC and compares multiple files
"""

import tkinter as tk
from ui.application import RespiratoryAnalysisToolkit
import os
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for plotting

def setup_environment():
    """Set up environment variables and configurations"""
    # Add the project root directory to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def main():
    """Main function to start the application"""
    setup_environment()
    
    # Initialize Tkinter root
    root = tk.Tk()
    
    # Create and start application
    app = RespiratoryAnalysisToolkit(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()