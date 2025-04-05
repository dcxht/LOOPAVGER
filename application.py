"""
Respiratory Data Processor
Main application class
"""

import tkinter as tk
from tkinter import ttk, Label, Frame, Button
import os

from ui.data_formatter import DataFormatterInterface
from ui.fvavg_interface import FVAvgInterface
from ui.data_processor_interface import DataProcessorInterface
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT

class RespiratoryAnalysisToolkit:
    def __init__(self, root):
        """
        Initialize the Respiratory Analysis Toolkit application
        
        Parameters:
        root - Tkinter root window
        """
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(True, True)
        
        # Apply a common style
        self.setup_styles()
        
        # Create UI elements
        self.create_widgets()
        
    def setup_styles(self):
        """Setup styles for the UI elements"""
        # Configure ttk styles
        self.style = ttk.Style()
        
        # Configure button styles
        self.style.configure(
            "Tool.TButton",
            font=("Arial", 11),
            padding=10
        )
        
        # Configure frame styles
        self.style.configure(
            "ToolFrame.TFrame",
            background="#f5f5f5"
        )
        
    def create_widgets(self):
        """Create and arrange all UI widgets"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = Label(main_frame, text=APP_TITLE, font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = Label(
            main_frame, 
            text="Comprehensive toolkit for respiratory data analysis", 
            font=("Arial", 10, "italic")
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Tools description
        tools_frame = ttk.Frame(main_frame, style="ToolFrame.TFrame")
        tools_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tool 1: Data Formatter
        tool1_frame = ttk.Frame(tools_frame, padding=10)
        tool1_frame.pack(fill='x', padx=10, pady=10)
        
        tool1_title = Label(tool1_frame, text="1. Data Formatter", font=("Arial", 12, "bold"))
        tool1_title.pack(anchor='w')
        
        tool1_desc = Label(
            tool1_frame, 
            text="Convert raw respiratory data files to the proper format for analysis.\n"
                 "Extracts flow and volume data from unprocessed files and creates standardized output.",
            justify='left',
            wraplength=APP_WIDTH-100
        )
        tool1_desc.pack(fill='x', pady=5)
        
        tool1_button = ttk.Button(
            tool1_frame, 
            text="Open Data Formatter", 
            command=self.open_data_formatter,
            style="Tool.TButton"
        )
        tool1_button.pack(pady=5)
        
        # Tool 2: Flow-Volume Averaging
        tool2_frame = ttk.Frame(tools_frame, padding=10)
        tool2_frame.pack(fill='x', padx=10, pady=10)
        
        tool2_title = Label(tool2_frame, text="2. Flow-Volume Averaging (FVAvg)", font=("Arial", 12, "bold"))
        tool2_title.pack(anchor='w')
        
        tool2_desc = Label(
            tool2_frame, 
            text="Analyze respiratory flow-volume data through advanced breath detection.\n"
                 "Identifies individual breaths, processes data using time-bin and volume-bin methods, "
                 "and generates statistical analysis with visualizations.",
            justify='left',
            wraplength=APP_WIDTH-100
        )
        tool2_desc.pack(fill='x', pady=5)
        
        tool2_button = ttk.Button(
            tool2_frame, 
            text="Open Flow-Volume Averaging", 
            command=self.open_fvavg,
            style="Tool.TButton"
        )
        tool2_button.pack(pady=5)
        
        # Tool 3: Data Processor
        tool3_frame = ttk.Frame(tools_frame, padding=10)
        tool3_frame.pack(fill='x', padx=10, pady=10)
        
        tool3_title = Label(tool3_frame, text="3. Data Processor", font=("Arial", 12, "bold"))
        tool3_title.pack(anchor='w')
        
        tool3_desc = Label(
            tool3_frame, 
            text="Convert volume measurements to percentage of Total Lung Capacity (TLC).\n"
                 "Compare multiple patient files side by side and generate averaged results.",
            justify='left',
            wraplength=APP_WIDTH-100
        )
        tool3_desc.pack(fill='x', pady=5)
        
        tool3_button = ttk.Button(
            tool3_frame, 
            text="Open Data Processor", 
            command=self.open_data_processor,
            style="Tool.TButton"
        )
        tool3_button.pack(pady=5)
        
        # Footer frame
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill='x', pady=(20, 0))
        
        # Exit button
        exit_button = ttk.Button(footer_frame, text="Exit", command=self.root.destroy)
        exit_button.pack(side='right')
    
    def open_data_formatter(self):
        """Open the Data Formatter interface"""
        data_formatter = DataFormatterInterface(self.root)
    
    def open_fvavg(self):
        """Open the Flow-Volume Averaging interface"""
        fvavg_interface = FVAvgInterface(self.root)
    
    def open_data_processor(self):
        """Open the Data Processor interface"""
        data_processor = DataProcessorInterface(self.root)