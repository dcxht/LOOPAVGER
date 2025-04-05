"""
Respiratory Data Processor
Data Processor Interface - Converts volume to % of TLC and arranges files side by side
"""

import tkinter as tk
from tkinter import Label, Entry, Button, StringVar, filedialog, messagebox, BooleanVar
from tkinter import Frame, Listbox, Scrollbar, END, Radiobutton, Checkbutton
import threading
import os

from ui.dialogs import TLCDialog, SubjectIDDialog
from data.processor import process_files
from utils.helpers import extract_subject_id
from config import (
    DEFAULT_EXTENSION, EXCEL_FILETYPES, OUTPUT_HORIZONTAL, 
    OUTPUT_SEPARATE, DEFAULT_OUTPUT_MESSAGE
)

class DataProcessorInterface:
    """Interface for the Data Processor functionality"""
    
    def __init__(self, parent):
        """
        Initialize the Data Processor interface
        
        Parameters:
        parent - Parent tkinter window
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Data Processor")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # File paths list
        self.selected_files = []
        # Dictionary to store TLC values for each file
        self.tlc_values = {}
        # Dictionary to store Subject IDs for each file
        self.subject_ids = {}
        
        # Output directory variable
        self.output_dir = StringVar()
        self.output_dir.set(DEFAULT_OUTPUT_MESSAGE)
        
        # Processing status variable
        self.status_var = StringVar()
        self.status_var.set("Ready")
        
        # Output option variable
        self.output_option = StringVar()
        self.output_option.set(OUTPUT_HORIZONTAL)  # default to horizontal layout
        
        # Auto-extract subject ID option
        self.auto_extract_id = BooleanVar(value=True)
        
        # Track processed output path
        self.processed_output_path = None
        
        # Create UI elements
        self.create_widgets()
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
    def create_widgets(self):
        """Create and arrange all UI widgets"""
        # Main frame with padding
        main_frame = Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = Label(main_frame, text="Data Processor", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Subtitle
        subtitle_label = Label(main_frame, text="Converts volume data to % of TLC and arranges files side by side", 
                              font=("Arial", 9, "italic"))
        subtitle_label.grid(row=0, column=0, columnspan=3, pady=(20, 0))
        
        # Files selection frame
        file_frame = Frame(main_frame)
        file_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        
        file_label = Label(file_frame, text="Excel Files:")
        file_label.grid(row=0, column=0, sticky="w")
        
        # File list with scrollbar
        list_frame = Frame(file_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = Listbox(list_frame, height=8, width=60, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # File buttons frame
        btn_frame = Frame(file_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="w")
        
        add_file_btn = Button(btn_frame, text="Add Files...", command=self.add_files)
        add_file_btn.pack(side="left", padx=5)
        
        clear_files_btn = Button(btn_frame, text="Clear Selection", command=self.clear_files)
        clear_files_btn.pack(side="left", padx=5)
        
        set_tlc_btn = Button(btn_frame, text="Set TLC Values...", command=self.set_tlc_values)
        set_tlc_btn.pack(side="left", padx=5)
        
        set_subject_btn = Button(btn_frame, text="Set Subject IDs...", command=self.set_subject_ids)
        set_subject_btn.pack(side="left", padx=5)
        
        # Auto-extract subject ID option
        auto_id_check = Checkbutton(file_frame, text="Auto-extract Subject IDs from filenames", 
                                 variable=self.auto_extract_id, command=self.update_auto_subject_ids)
        auto_id_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Output directory variable
        output_label = Label(main_frame, text="Output:")
        output_label.grid(row=2, column=0, sticky="w", pady=5)
        
        output_path_label = Label(main_frame, textvariable=self.output_dir, width=45, anchor="w", bg="#f0f0f0", relief="sunken", padx=5)
        output_path_label.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")
        
        # Set output file button
        set_output_btn = Button(main_frame, text="Set Output File", command=self.set_output_location)
        set_output_btn.grid(row=2, column=2, sticky="e")
        
        # Output option - consolidated or separate
        output_option_label = Label(main_frame, text="Output Format:")
        output_option_label.grid(row=3, column=0, sticky="w", pady=5)
        
        output_option_frame = Frame(main_frame)
        output_option_frame.grid(row=3, column=1, sticky="w")
        
        horizontal_option = Radiobutton(output_option_frame, 
                                       text="Horizontal Layout (Files Side by Side)", 
                                       variable=self.output_option, 
                                       value=OUTPUT_HORIZONTAL)
        horizontal_option.pack(anchor="w")
        
        separate_files_option = Radiobutton(output_option_frame, 
                                           text="Separate File For Each Input", 
                                           variable=self.output_option, 
                                           value=OUTPUT_SEPARATE)
        separate_files_option.pack(anchor="w")
        
        # Instructions
        instructions = Label(main_frame, text="This tool converts respiratory volume data to a percentage of TLC.\n"
                                             "The Excel files should contain inspiration/expiration\n"
                                             "volume and flow data in the 'Avg Vol Bin Data' sheet.\n"
                                             "Data from different files will be arranged side by side.",
                            justify="left", font=("Arial", 9))
        instructions.grid(row=4, column=0, columnspan=3, pady=10, sticky="w")
        
        # Button frame
        button_frame = Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Process button
        process_button = Button(button_frame, text="Process Files", command=self.start_processing, 
                               width=15, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        process_button.pack(side="left", padx=10)
        
        # Generate Plots button - disabled initially
        self.plot_button = Button(button_frame, text="Generate Plots", command=self.generate_plots,
                               width=15, bg="#4C75AF", fg="white", font=("Arial", 10), state="disabled")
        self.plot_button.pack(side="left", padx=10)
        
        # Close button
        close_button = Button(button_frame, text="Close", command=self.window.destroy, width=10)
        close_button.pack(side="left", padx=10)
        
        # Status bar
        status_bar = Label(main_frame, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        status_bar.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
    def add_files(self):
        """Open file dialog to select multiple Excel files"""
        files = filedialog.askopenfilenames(
            title="Select Excel Files",
            filetypes=EXCEL_FILETYPES
        )
        
        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    # Show just the file name in the listbox, not the full path
                    self.file_listbox.insert(END, os.path.basename(file_path))
            
            # If auto-extract is enabled, extract subject IDs
            if self.auto_extract_id.get():
                self.update_auto_subject_ids()
    
    def update_auto_subject_ids(self):
        """Update subject IDs based on file names if auto-extract is enabled"""
        if self.auto_extract_id.get():
            # Extract IDs for all files that don't already have manually set IDs
            auto_extracted = 0
            for file_path in self.selected_files:
                if file_path not in self.subject_ids or not self.subject_ids[file_path]:
                    subject_id = extract_subject_id(file_path)
                    if subject_id:
                        self.subject_ids[file_path] = subject_id
                        auto_extracted += 1
            
            if auto_extracted > 0:
                self.status_var.set(f"Auto-extracted {auto_extracted} subject IDs from filenames.")
    
    def clear_files(self):
        """Clear all selected files"""
        self.file_listbox.delete(0, END)
        self.selected_files = []
        self.tlc_values = {}
        self.subject_ids = {}
        self.processed_output_path = None
        self.plot_button.config(state="disabled")
        
    def set_tlc_values(self):
        """Set individual TLC values for each file"""
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one Excel file first.")
            return
        
        # Open the TLC dialog and get values
        dialog = TLCDialog(self.window, self.selected_files, self.tlc_values)
        self.window.wait_window(dialog.window)
        
        # Update values if dialog was not cancelled
        if dialog.result:
            self.tlc_values = dialog.result
            self.status_var.set(f"TLC values set for {len(self.tlc_values)} files.")
    
    def set_subject_ids(self):
        """Set individual Subject IDs for each file"""
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one Excel file first.")
            return
        
        # Open the Subject ID dialog and get values
        dialog = SubjectIDDialog(self.window, self.selected_files, self.subject_ids)
        self.window.wait_window(dialog.window)
        
        # Update values if dialog was not cancelled
        if dialog.result:
            self.subject_ids = dialog.result
            self.status_var.set(f"Subject IDs set for {len(self.subject_ids)} files.")
    
    def set_output_location(self):
        """Set the output file location"""
        file_path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=DEFAULT_EXTENSION,
            filetypes=EXCEL_FILETYPES
        )
        
        if file_path:
            self.output_dir.set(file_path)
            
    def start_processing(self):
        """Start processing in a separate thread"""
        # Check if files are selected
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one Excel file.")
            return
        
        # Check if we have TLC values for all files
        missing_tlc = []
        for file_path in self.selected_files:
            if file_path not in self.tlc_values:
                missing_tlc.append(os.path.basename(file_path))
                    
        if missing_tlc:
            messagebox.showerror("Error", 
                               f"Missing TLC values for the following files:\n{', '.join(missing_tlc)}\n\n"
                               f"Please use 'Set TLC Values...' to set individual TLC values.")
            return
        
        # Check output location if using horizontal layout
        output_option = self.output_option.get()
        if output_option == OUTPUT_HORIZONTAL and self.output_dir.get() == DEFAULT_OUTPUT_MESSAGE:
            # Prompt user to set output location
            self.set_output_location()
            if self.output_dir.get() == DEFAULT_OUTPUT_MESSAGE:
                messagebox.showerror("Error", "Please select an output file location.")
                return
        
        # Disable plot button during processing
        self.plot_button.config(state="disabled")
        
        # Start processing in a separate thread
        self.status_var.set("Processing...")
        thread = threading.Thread(
            target=self.run_processing_thread,
            args=(
                self.selected_files,
                self.tlc_values,
                self.subject_ids,
                self.output_option.get(),
                self.output_dir.get()
            )
        )
        thread.daemon = True
        thread.start()
    
    def run_processing_thread(self, selected_files, tlc_values, subject_ids, output_option, output_path):
        """Run the processing in a separate thread"""
        try:
            # Process the files
            result = process_files(selected_files, tlc_values, subject_ids, output_option, output_path)
            
            # Update the UI with the results
            self.window.after(0, lambda: self.processing_complete(result))
        except Exception as e:
            # Handle any exceptions
            self.window.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.window.after(0, lambda: self.status_var.set("Error during processing."))
    
    def processing_complete(self, result):
        """Update the UI after processing is complete"""
        successful_files = result.get('successful_files', [])
        failed_files = result.get('failed_files', [])
        output_path = result.get('output_path', '')
        
        if failed_files:
            self.status_var.set(f"Completed with errors. {len(successful_files)} succeeded, {len(failed_files)} failed.")
            error_msg = "The following files could not be processed:\n" + "\n".join(failed_files)
            messagebox.showwarning("Processing Incomplete", error_msg)
        else:
            self.status_var.set(f"Processing complete. All {len(successful_files)} files processed successfully.")
            
            # Enable plot button if horizontal layout was used (all data in one file)
            if self.output_option.get() == OUTPUT_HORIZONTAL:
                self.plot_button.config(state="normal")
                self.processed_output_path = output_path  # Store output path for plot generation
                
                messagebox.showinfo("Success", 
                                  f"All files processed successfully!\n\n"
                                  f"{len(successful_files)} files processed and saved to:\n{output_path}")
            else:
                messagebox.showinfo("Success", f"All files processed successfully!\n\n{len(successful_files)} files processed.")
    
    def generate_plots(self):
        """Generate plots from the processed data"""
        if hasattr(self, 'processed_output_path') and os.path.exists(self.processed_output_path):
            # Ask user where to save the plots
            output_dir = filedialog.askdirectory(
                title="Select Directory to Save Plots"
            )
            
            if not output_dir:
                return
                
            # Update status
            self.status_var.set("Generating plots...")
            
            # Import the graph generator module
            from ui import graph_generator
            
            # Call the graph generator function
            try:
                results = graph_generator.generate_plots_from_file(
                    self.processed_output_path, output_dir
                )
                
                if results.get('error'):
                    messagebox.showerror("Error", results['error'])
                    self.status_var.set("Error generating plots.")
                else:
                    self.status_var.set(f"Saved {results['saved_count']} plots to {output_dir}")
                    messagebox.showinfo(
                        "Success", 
                        f"Generated and saved {results['saved_count']} plots to {output_dir}"
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Error calling graph generator: {str(e)}")
                self.status_var.set("Error generating plots.")
        else:
            messagebox.showinfo("Info", "Please process files first (using Horizontal Layout) before generating plots.")