"""
Respiratory Data Processor
Dialog windows for TLC and Subject ID input
"""

import tkinter as tk
from tkinter import Label, Entry, Button, StringVar, Frame, messagebox
import os

class TLCDialog:
    """Dialog for setting TLC values for each file"""
    def __init__(self, parent, file_paths, existing_values=None):
        self.parent = parent
        self.file_paths = file_paths
        self.existing_values = existing_values or {}
        self.result = None  # Will hold the result dictionary if Apply is clicked
        
        # Create the dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Set TLC Values")
        self.window.geometry("400x400")
        
        # Create UI elements
        self.create_widgets()
        
        # Make the window modal
        self.window.grab_set()
    
    def create_widgets(self):
        # Create a frame for the TLC entries
        tlc_frame = Frame(self.window, padx=20, pady=20)
        tlc_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = Label(tlc_frame, text="Set Individual TLC Values", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create entry fields for each file
        row = 1
        self.tlc_entries = {}
        
        for file_path in self.file_paths:
            filename = os.path.basename(file_path)
            label = Label(tlc_frame, text=filename, anchor="w")
            label.grid(row=row, column=0, sticky="w", pady=5)
            
            # Create StringVar and Entry for the TLC value
            tlc_var = StringVar()
            # Use existing value if it exists
            if file_path in self.existing_values:
                tlc_var.set(str(self.existing_values[file_path]))
            else:
                tlc_var.set("")
                
            entry = Entry(tlc_frame, textvariable=tlc_var, width=10)
            entry.grid(row=row, column=1, sticky="w", pady=5)
            
            self.tlc_entries[file_path] = tlc_var
            row += 1
        
        # Button frame
        button_frame = Frame(tlc_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        apply_button = Button(button_frame, text="Apply", command=self.apply_values, bg="#4CAF50", fg="white", width=10)
        apply_button.pack(side="left", padx=10)
        
        cancel_button = Button(button_frame, text="Cancel", command=self.window.destroy, width=10)
        cancel_button.pack(side="left", padx=10)
    
    def apply_values(self):
        """Process and validate the entered values"""
        has_error = False
        result = {}
        
        for file_path, tlc_var in self.tlc_entries.items():
            tlc_str = tlc_var.get().strip()
            if tlc_str:  # Only process if a value was entered
                try:
                    tlc_value = float(tlc_str)
                    if tlc_value <= 0:
                        messagebox.showerror("Error", f"TLC must be a positive number for {os.path.basename(file_path)}")
                        has_error = True
                        break
                    result[file_path] = tlc_value
                except ValueError:
                    messagebox.showerror("Error", f"Invalid TLC value for {os.path.basename(file_path)}")
                    has_error = True
                    break
        
        if not has_error:
            self.result = result
            self.window.destroy()

class SubjectIDDialog:
    """Dialog for setting Subject IDs for each file"""
    def __init__(self, parent, file_paths, existing_values=None):
        self.parent = parent
        self.file_paths = file_paths
        self.existing_values = existing_values or {}
        self.result = None  # Will hold the result dictionary if Apply is clicked
        
        # Create the dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Set Subject IDs")
        self.window.geometry("400x400")
        
        # Create UI elements
        self.create_widgets()
        
        # Make the window modal
        self.window.grab_set()
    
    def create_widgets(self):
        # Create a frame for the Subject ID entries
        subject_frame = Frame(self.window, padx=20, pady=20)
        subject_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = Label(subject_frame, text="Set Individual Subject IDs", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create entry fields for each file
        row = 1
        self.subject_entries = {}
        
        for file_path in self.file_paths:
            filename = os.path.basename(file_path)
            label = Label(subject_frame, text=filename, anchor="w")
            label.grid(row=row, column=0, sticky="w", pady=5)
            
            # Create StringVar and Entry for the Subject ID
            subject_var = StringVar()
            # Use existing value if it exists
            if file_path in self.existing_values:
                subject_var.set(str(self.existing_values[file_path]))
            else:
                subject_var.set("")
                
            entry = Entry(subject_frame, textvariable=subject_var, width=10)
            entry.grid(row=row, column=1, sticky="w", pady=5)
            
            self.subject_entries[file_path] = subject_var
            row += 1
        
        # Button frame
        button_frame = Frame(subject_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        apply_button = Button(button_frame, text="Apply", command=self.apply_values, bg="#4CAF50", fg="white", width=10)
        apply_button.pack(side="left", padx=10)
        
        cancel_button = Button(button_frame, text="Cancel", command=self.window.destroy, width=10)
        cancel_button.pack(side="left", padx=10)
    
    def apply_values(self):
        """Process the entered values"""
        result = {}
        
        for file_path, subject_var in self.subject_entries.items():
            subject_str = subject_var.get().strip()
            if subject_str:  # Only process if a value was entered
                result[file_path] = subject_str
        
        self.result = result
        self.window.destroy()