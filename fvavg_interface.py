"""
Respiratory Data Processor
UI interface for Flow-Volume Averaging (FVAvg) functionality
"""

import tkinter as tk
from tkinter import Label, Entry, Button, StringVar, filedialog, messagebox, Frame, IntVar
import threading
import os

from analysis.fvavg import process_fvavg, process_max_loop, generate_plots

class FVAvgInterface:
    """Interface for the Flow-Volume Averaging functionality"""
    
    def __init__(self, parent):
        """
        Initialize the FVAvg interface
        
        Parameters:
        parent - Parent tkinter window
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Flow-Volume Averaging")
        self.window.geometry("600x700")
        self.window.resizable(True, True)
        
        # Data variables
        self.input_file = StringVar()
        self.output_file = StringVar()
        self.intervals = IntVar(value=100)
        self.max_loop_file = StringVar()
        self.status_var = StringVar(value="Ready")
        self.fvavg_results = None
        
        # Create UI elements
        self.create_widgets()
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
    def create_widgets(self):
        """Create and arrange all UI widgets"""
        main_frame = Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = Label(main_frame, text="Flow-Volume Averaging", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        input_label = Label(main_frame, text="Input File:", anchor="w")
        input_label.grid(row=1, column=0, sticky="w", pady=5)
        
        input_path_label = Label(main_frame, textvariable=self.input_file, width=40, 
                               anchor="w", bg="#f0f0f0", relief="sunken", padx=5)
        input_path_label.grid(row=1, column=1, pady=5, sticky="w")
        
        input_btn = Button(main_frame, text="Browse...", command=self.browse_input_file)
        input_btn.grid(row=1, column=2, padx=5)
        
        # Output file selection
        output_label = Label(main_frame, text="Output File:", anchor="w")
        output_label.grid(row=2, column=0, sticky="w", pady=5)
        
        output_path_label = Label(main_frame, textvariable=self.output_file, width=40, 
                                anchor="w", bg="#f0f0f0", relief="sunken", padx=5)
        output_path_label.grid(row=2, column=1, pady=5, sticky="w")
        
        output_btn = Button(main_frame, text="Browse...", command=self.browse_output_file)
        output_btn.grid(row=2, column=2, padx=5)
        
        # Intervals
        intervals_label = Label(main_frame, text="Intervals:", anchor="w")
        intervals_label.grid(row=3, column=0, sticky="w", pady=5)
        
        intervals_entry = Entry(main_frame, textvariable=self.intervals, width=10)
        intervals_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        intervals_help = Label(main_frame, text="Number of intervals to divide each breath into", 
                             font=("Arial", 8, "italic"))
        intervals_help.grid(row=3, column=1, sticky="e", columnspan=2)
        
        # Max loop file selection
        max_loop_label = Label(main_frame, text="Max Loop File (Optional):", anchor="w")
        max_loop_label.grid(row=4, column=0, sticky="w", pady=5)
        
        max_loop_path_label = Label(main_frame, textvariable=self.max_loop_file, width=40, 
                                  anchor="w", bg="#f0f0f0", relief="sunken", padx=5)
        max_loop_path_label.grid(row=4, column=1, pady=5, sticky="w")
        
        max_loop_btn = Button(main_frame, text="Browse...", command=self.browse_max_loop_file)
        max_loop_btn.grid(row=4, column=2, padx=5)
        
        # Instructions
        instruction_frame = Frame(main_frame, bd=1, relief="solid", padx=10, pady=10)
        instruction_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=15)
        
        instructions = Label(instruction_frame, text=(
            "Flow-Volume Averaging (FVAvg) analyzes respiratory flow-volume data by:\n"
            "1. Finding zero-flow points to identify inspiration and expiration phases\n"
            "2. Averaging data using both time-based and volume-based methods\n"
            "3. Generating statistical measures and visualizations of breathing patterns\n\n"
            "Input files should contain Time, Vol, and Flow columns."
        ), justify="left")
        instructions.pack(anchor="w")
        
        # Button frame
        button_frame = Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Process button
        process_btn = Button(button_frame, text="Process File", command=self.process_file, 
                           width=15, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        process_btn.pack(side="left", padx=10)
        
        # Generate plots button (initially disabled)
        self.plots_btn = Button(button_frame, text="Generate Plots", command=self.generate_plots, 
                              width=15, state="disabled")
        self.plots_btn.pack(side="left", padx=10)
        
        # Close button
        close_btn = Button(button_frame, text="Close", command=self.window.destroy, width=10)
        close_btn.pack(side="left", padx=10)
        
        # Status bar
        status_bar = Label(main_frame, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        status_bar.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(10, 0))
    
    def browse_input_file(self):
        """Open file dialog to select input Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            self.input_file.set(file_path)
            
            # Auto-set output file if not already set
            if not self.output_file.get():
                input_dir = os.path.dirname(file_path)
                input_name = os.path.splitext(os.path.basename(file_path))[0]
                self.output_file.set(os.path.join(input_dir, f"{input_name}_processed.xlsx"))
    
    def browse_output_file(self):
        """Open file dialog to select output Excel file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            self.output_file.set(file_path)
    
    def browse_max_loop_file(self):
        """Open file dialog to select max loop Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Max Loop Excel File",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            self.max_loop_file.set(file_path)
    
    def process_file(self):
        """Process the input file using FVAvg"""
        # Validate input
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        try:
            intervals = int(self.intervals.get())
            if intervals <= 0:
                messagebox.showerror("Error", "Number of intervals must be positive.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of intervals.")
            return
        
        # Start processing in a separate thread
        self.status_var.set("Processing...")
        thread = threading.Thread(
            target=self.run_processing_thread
        )
        thread.daemon = True
        thread.start()
    
    def run_processing_thread(self):
        """Run the processing in a separate thread"""
        try:
            # Process the file
            self.fvavg_results = process_fvavg(
                file_path=self.input_file.get(),
                intervals=self.intervals.get(),
                output_filename=self.output_file.get()
            )
            
            # Process max loop if specified
            if self.max_loop_file.get():
                try:
                    fig = process_max_loop(
                        self.fvavg_results,
                        self.max_loop_file.get()
                    )
                    
                    # Save the figure
                    output_dir = os.path.dirname(self.output_file.get())
                    base_name = os.path.splitext(os.path.basename(self.output_file.get()))[0]
                    plot_path = os.path.join(output_dir, f"{base_name}_max_loop_comparison.png")
                    fig.savefig(plot_path)
                    
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showwarning(
                        "Max Loop Processing Warning", 
                        f"Could not process max loop file: {str(e)}"
                    ))
            
            # Update UI
            self.window.after(0, self.processing_complete)
            
        except Exception as e:
            # Handle any exceptions
            self.window.after(0, lambda: messagebox.showerror(
                "Error", f"An error occurred during processing: {str(e)}"
            ))
            self.window.after(0, lambda: self.status_var.set("Error during processing."))
    
    def processing_complete(self):
        """Update the UI after processing is complete"""
        self.status_var.set(f"Processing complete. Data saved to {self.output_file.get()}")
        
        # Enable the generate plots button
        self.plots_btn.config(state="normal")
        
        # Show success message
        messagebox.showinfo(
            "Processing Complete", 
            f"Flow-Volume Averaging complete!\n\n"
            f"Processed {self.fvavg_results['number_of_breaths']} breaths with "
            f"{self.fvavg_results['intervals']} intervals.\n\n"
            f"Results saved to:\n{self.output_file.get()}"
        )
    
    def generate_plots(self):
        """Generate and save plots from the FVAvg results"""
        if not self.fvavg_results:
            messagebox.showerror("Error", "No processed results available. Please process a file first.")
            return
        
        # Ask for output directory
        output_dir = filedialog.askdirectory(
            title="Select Directory for Plot Images"
        )
        
        if not output_dir:
            return
        
        try:
            # Generate plots
            self.status_var.set("Generating plots...")
            plot_files = generate_plots(self.fvavg_results, output_dir)
            
            # Update UI
            self.status_var.set(f"Generated {len(plot_files)} plots in {output_dir}")
            
            # Show success message
            messagebox.showinfo(
                "Plots Generated", 
                f"Successfully generated {len(plot_files)} plots!\n\n"
                f"Plot images saved to:\n{output_dir}"
            )
            
        except Exception as e:
            # Handle any exceptions
            messagebox.showerror("Error", f"An error occurred while generating plots: {str(e)}")
            self.status_var.set("Error generating plots.")