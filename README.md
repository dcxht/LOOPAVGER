# Respiratory Analysis Toolkit

## Comprehensive Technical Documentation

This document provides an in-depth explanation of the Respiratory Analysis Toolkit, detailing the internal logic, equations, functions, and processing methods used throughout the application.

## Table of Contents

1. [Application Overview](#application-overview)
2. [Tool 1: Data Formatter](#tool-1-data-formatter)
3. [Tool 2: Flow-Volume Averaging (FVAvg)](#tool-2-flow-volume-averaging-fvavg)
4. [Tool 3: Data Processor](#tool-3-data-processor)
5. [Technical Implementation Details](#technical-implementation-details)
6. [Mathematical Equations and Algorithms](#mathematical-equations-and-algorithms)
7. [Data Structures and File Formats](#data-structures-and-file-formats)
8. [Configuration Settings](#configuration-settings)
9. [Troubleshooting and FAQ](#troubleshooting-and-faq)

---

## Application Overview

The Respiratory Analysis Toolkit is a comprehensive suite of tools designed for medical researchers and healthcare professionals who work with respiratory data. The application consists of three integrated tools that form a complete workflow for respiratory data analysis:

1. **Data Formatter**: Converts raw respiratory data files to a standardized format
2. **Flow-Volume Averaging (FVAvg)**: Performs advanced breath-by-breath analysis
3. **Data Processor**: Converts volume to percentage of Total Lung Capacity (TLC) and compares multiple files

This application requires Python 3.6 or higher with dependencies including pandas, numpy, matplotlib, openpyxl, and tkinter.

---

## Tool 1: Data Formatter

### Purpose

The Data Formatter tool converts raw respiratory data files from laboratory equipment into a standardized format suitable for further analysis. It extracts flow and volume measurements and organizes them with standardized time intervals.

### Behind the Scenes: Data Formatter Logic

#### Function: `convert_unedited_file()`

This function processes a raw respiratory data file through the following steps:

1. **File Reading**:
   ```python
   wb = load_workbook(input_file)  # Load Excel workbook
   ws = wb.active                  # Get active worksheet
   ```

2. **Data Extraction Logic**:
   - The function iterates through each row in the worksheet
   - It looks for marker rows containing "ltr/s" (for flow data) and "ltr" (for volume data)
   - When a marker is found, it sets a flag to start collecting the corresponding data type
   - It handles header rows by using skip flags
   - Data collection stops when it encounters an empty row

   ```python
   # Example: Flow data extraction
   if start_collecting_flow:
       if first_column == "":  # Empty row signals end of data section
           start_collecting_flow = False
       else:
           try:
               flow_values.append(float(first_column))
           except (ValueError, TypeError):
               pass  # Skip non-numeric values
   ```

3. **Time Interval Creation**:
   - Creates uniform time intervals at 0.01 second increments
   - Time points are calculated as: time = 0.01 * index
   
   ```python
   time_data = [round(0.01 * i, 2) for i in range(1, len(flow_values) + 1)]
   ```

4. **Standardized Output Format**:
   - Creates a pandas DataFrame with three columns: Time, Vol, Flow
   - Ensures all columns have the same length by trimming if necessary
   
   ```python
   processed_data = pd.DataFrame({
       "Time": time_data,
       "Vol": volume_values[:len(time_data)],  # Trim to match time length
       "Flow": flow_values[:len(time_data)]    # Trim to match time length
   })
   ```

5. **Data Format Validation**:
   - The function assumes that flow data follows the "ltr/s" marker
   - Volume data follows the "ltr" marker
   - Time values are created artificially rather than extracted

#### Batch Processing Implementation

The batch processing capability processes multiple files sequentially, with error handling for each file:

```python
for input_file in self.selected_files:
    try:
        # Process each file
        output_file = os.path.join(output_dir, f"{base_name}_formatted.xlsx")
        self.convert_unedited_file(input_file, output_file)
        successful_files.append(os.path.basename(input_file))
    except Exception as e:
        failed_files.append(f"{os.path.basename(input_file)} (Error: {str(e)})")
```

---

## Tool 2: Flow-Volume Averaging (FVAvg)

### Purpose

The Flow-Volume Averaging (FVAvg) tool performs in-depth respiratory analysis by:
1. Automatically detecting individual breaths
2. Separating inspiration and expiration phases
3. Analyzing breaths using both time-based and volume-based methods
4. Generating statistical measures and visualizations

### Behind the Scenes: FVAvg Logic

#### Function: `find_zero_flow_points()`

This function identifies transition points between inspiration and expiration by finding where flow crosses zero:

1. **Identifying Zero-Flow Transitions**:
   - Detects when flow changes from negative to positive (start of inspiration)
   - Detects when flow changes from positive to negative (start of expiration)
   - Adds interpolated zero-flow points to the data
   
   ```python
   # Example: Detecting negative to positive flow transition
   if flow_raw_list[i] < 0 < flow_raw_list[i + 1]:
       # Additional validation checks...
       
       # Linear interpolation to find exact time of zero flow
       interpolated_time = t1 + ((0 - f1) / ((f2 - f1) / (t2 - t1)))
       
       # Add zero-flow point
       zeroed_time_list.append(interpolated_time)
       zeroed_flow_list.append(0)
       zeroed_vol_list.append(interpolated_volume)
   ```

2. **Validation Criteria**:
   - Checks if the transition is sustained (not just noise)
   - Examines 30 future values to confirm direction
   - Examines previous 20 values to verify prior flow direction
   
   ```python
   # Validation checks
   counter = 0
   for j in range(1, 31):  # Check next 30 values
       if flow_raw_list[i + 1 + j] > 0:
           counter = counter + 1
   
   back_track = 0
   for j in range(41, 61):  # Check previous values
       try:
           back_track = flow_raw_list[i - j] + back_track
       except IndexError:
           pass
   
   back_track = back_track / 20
   
   # Only interpolate if both checks pass
   if counter == 30 and back_track < 0:
       # Interpolation code...
   ```

3. **Mathematical Interpolation**:
   - Uses linear interpolation to estimate the exact time where flow = 0
   - The interpolation equation: 
     ```
     interpolated_time = t1 + ((0 - f1) / ((f2 - f1) / (t2 - t1)))
     ```
   - Where t1, t2 are times and f1, f2 are flow values at adjacent points

#### Function: `process_time_bins()`

This function divides each breath into equal time intervals for standardized analysis:

1. **Breath Separation**:
   - Separates inspiration and expiration data for each breath
   - Uses phase indexes to identify different phases of breathing
   
   ```python
   # Extract inspiration time
   while phase_limit < phase_indexes_list[0]:
       zeroed_time_list[0] = zeroed_time_list[0] - Time_subtract_value_insp
       Insp_Time.append(zeroed_time_list[0])
       del zeroed_time_list[0]
       phase_limit += 1
   ```

2. **Time Interval Calculation**:
   - Divides the total time of each breath phase by the specified number of intervals
   - Creates equal time points for inspiration and expiration phases
   
   ```python
   # Calculate time intervals for inspiration
   insp_time_intervals_tbins = []
   incr_insp_time = Tt_Insp_list[i] / intervals
   for j in range(intervals + 1):
       Tt_insp_value = incr_insp_time * j
       insp_time_intervals_tbins.append(Tt_insp_value)
   ```

3. **Data Interpolation**:
   - For each time interval, interpolates volume and flow values
   - Uses linear interpolation between nearest measured points
   
   ```python
   # Example: Interpolation for inspiration volume and flow
   for j in range(len(insp_time_intervals_tbins)):
       Actual_Time_Interval = insp_time_intervals_tbins[j]
       for l in range(len(Insp_Time)):
           try:
               # Various conditions for interpolation...
               
               # Linear interpolation formula
               Volume_at_Interval = v1 + ((v2 - v1) / (t2 - t1)) * (Actual_Time_Interval - t1)
               Flow_at_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Actual_Time_Interval - t1)
           except IndexError:
               # Handle edge cases...
   ```

4. **Normalization Process**:
   - Shifts volume values to align at zero
   - Normalizes as percentage of tidal volume
   
   ```python
   # Normalize volume values
   for i in range(number_of_breaths):
       for j in range(intervals + 1):
           time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j] = (
               (time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j] / Vt_Insp_list[i]) * Avg_Insp_Vt
           )
   ```

5. **Statistical Calculations**:
   - Calculates averages across all breaths for each interval
   - Computes standard error of the mean (SEM) for statistical confidence
   
   ```python
   # Calculate average and SEM for inspiration volume
   Total_Insp_Volume = 0
   temp_sem = []
   for i in range(number_of_breaths):
       temp_sem.append(time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j])
       Total_Insp_Volume += time_bins_breath_dictionary[f"Breath_{i}"]["Insp_Vol"][j]
   temp_sem = np.array(temp_sem)
   x = np.std(temp_sem, ddof=1)  # Standard deviation with n-1 degrees of freedom
   avg_insp_vol_tbin_sem.append(x)
   Avg_Insp_Vol = (Total_Insp_Volume / number_of_breaths) + Mean_shift
   ```

#### Function: `process_volume_bins()`

This function analyzes breaths by dividing volume into equal intervals, rather than time:

1. **Volume Interval Creation**:
   - Divides the tidal volume into equal segments
   - Creates volume points at these increments
   
   ```python
   # Calculate volume bins for inspiration
   insp_vol_intervals_vbins = []
   incr_insp_vol = Vt_Insp_list[i] / intervals
   Start_Insp_Value = insp_vol[0]
   
   for j in range(intervals + 1):
       Vt_insp_value = incr_insp_vol * j
       Vt_insp_value = Start_Insp_Value - Vt_insp_value
       insp_vol_intervals_vbins.append(Vt_insp_value)
   ```

2. **Flow Interpolation at Volume Points**:
   - For each volume point, interpolates the corresponding flow value
   - Uses linear interpolation between measured points
   
   ```python
   # Interpolate flow values for inspiration at volume intervals
   for j in range(len(insp_vol_intervals_vbins)):
       Actual_Volume_Interval = insp_vol_intervals_vbins[j]
       for l in range(len(insp_vol)):
           try:
               # Various conditions for interpolation...
               
               # Linear interpolation for flow at specific volume
               Time_at_Volume_Interval = t1 + ((Actual_Volume_Interval - v1) / ((v2 - v1) / (t2 - t1)))
               Flow_at_Volume_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Time_at_Volume_Interval - t1)
           except IndexError:
               # Handle edge cases...
   ```

#### Visualization Functions

The FVAvg tool includes multiple visualization functions, each generating specific types of plots:

1. **Individual Breath Plots**: 
   - Shows each detected breath as a flow-volume loop
   - Different plots for time-bin and volume-bin methods
   
2. **Average Flow-Volume Loops**:
   - Plots average data with standard error bars
   - Separate plots for time-bin and volume-bin methods

3. **Comparison Plots**:
   - Overlays time-bin and volume-bin results for comparison
   - Can include max loop comparison if provided

4. **Original Data Plot**:
   - Shows original data with average curves superimposed
   - Helps visualize how individual breaths contribute to averages

---

## Tool 3: Data Processor

### Purpose

The Data Processor tool converts respiratory volume measurements to percentages of Total Lung Capacity (TLC) and provides multiple ways to analyze and compare data across patients.

### Behind the Scenes: Data Processor Logic

#### Function: `read_excel_file()`

This function reads respiratory data from Excel files:

1. **File Loading**:
   - Loads the Excel file using pandas
   - Checks for specific sheet names (e.g., "Avg Vol Bin Data")
   
   ```python
   # Check if target sheet exists
   if DEFAULT_SHEET in sheet_names:
       df = pd.read_excel(file_path, sheet_name=DEFAULT_SHEET)
   else:
       # If not, just read the first sheet
       df = pd.read_excel(file_path)
   ```

2. **Column Identification**:
   - Uses pattern matching to find appropriate columns
   - Looks for column names containing specific patterns (e.g., "insp", "vol")
   
   ```python
   # Find the required columns using pattern matching
   insp_vol_col = find_column(df, VOL_INSP_PATTERN)
   insp_flow_col = find_column(df, FLOW_INSP_PATTERN)
   exp_vol_col = find_column(df, VOL_EXP_PATTERN)
   exp_flow_col = find_column(df, FLOW_EXP_PATTERN)
   ```

3. **TLC Conversion**:
   - Stores raw volume data
   - Converts volume to percentage of TLC using the equation:
     `percent_vol = (raw_vol / tlc) * 100`
   
   ```python
   # Store raw volume data
   raw_insp_vol = df[insp_vol_col].copy()
   raw_exp_vol = df[exp_vol_col].copy()
   
   # Calculate percentage of TLC
   insp_vol_percent = (df[insp_vol_col] / tlc) * 100
   exp_vol_percent = (df[exp_vol_col] / tlc) * 100
   ```

#### Function: `process_files()`

This function orchestrates the processing of multiple files:

1. **Validation and Preparation**:
   - Checks that all files have TLC values assigned
   - Organizes file paths and metadata
   
2. **File Processing Loop**:
   - Processes each file individually
   - Collects data for subsequent aggregation
   
   ```python
   for file_path in selected_files:
       # Get the TLC value and subject ID
       tlc = tlc_values[file_path]
       subject_id = subject_ids.get(file_path, "")
       
       # Process the file
       insp_vol, insp_flow, exp_vol, exp_flow, n_rows, raw_insp_vol, raw_exp_vol, success = read_excel_file(file_path, tlc, subject_id)
       
       if success:
           # Store processed data
           processed_dfs[file_path] = {
               'insp_vol': insp_vol,
               'insp_flow': insp_flow,
               # ... other data ...
           }
   ```

3. **Output Generation**:
   - Creates separate files or horizontal layout based on user selection
   - Calls appropriate writer functions

#### Function: `create_horizontal_layout_output()`

This function creates consolidated output with multiple sheets:

1. **Data Aggregation**:
   - Combines data from multiple files side by side
   - Creates dictionaries for different data types (raw, percent TLC, absolute)
   
   ```python
   # Process each file to create side-by-side columns
   for i, file_path in enumerate(selected_files):
       if file_path in processed_dfs:
           file_data = processed_dfs[file_path]
           
           # Add to combined data with subject ID in column name
           vol_col_name = f"Vol % TLC {subject_id}" if subject_id else f"Vol % TLC {i+1}"
           combined_data[vol_col_name] = pd.concat([insp_vol, exp_vol], ignore_index=True)
           
           # Add to raw data
           raw_vol_col_name = f"Raw Vol {subject_id}" if subject_id else f"Raw Vol {i+1}"
           raw_data[raw_vol_col_name] = pd.concat([raw_insp_vol, raw_exp_vol], ignore_index=True)
   ```

2. **Average Calculations**:
   - Calculates average TLC across all files
   - Computes average volume and flow at each data point
   
   ```python
   # Calculate average TLC
   avg_tlc = sum(all_tlc_values) / len(all_tlc_values) if all_tlc_values else 0
   
   # Calculate average inspiration and expiration volumes
   avg_insp_vol = pd.concat(padded_insp_vols, axis=1).mean(axis=1, skipna=True)
   avg_exp_vol = pd.concat(padded_exp_vols, axis=1).mean(axis=1, skipna=True)
   ```

3. **Absolute Volume Calculations**:
   - Converts % TLC back to absolute volume using average TLC
   - Uses the equation: `absolute_vol = (percent_vol * avg_tlc) / 100`
   
   ```python
   # Convert % TLC to absolute volume
   for col in combined_df.columns:
       if 'Vol % TLC' in col:
           abs_col_name = col.replace('Vol % TLC', 'Absolute Vol')
           absolute_data[abs_col_name] = combined_df[col].apply(
               lambda x: (float(x) * avg_tlc / 100) if pd.notnull(x) and x != "" else x
           )
   ```

4. **Normalized Average Data**:
   - Creates normalized averages using average TLC
   - Same conversion formula as absolute volume
   
   ```python
   # Normalize the average volume data
   norm_avg_vol = avg_df['Average Vol % TLC'].apply(
       lambda x: (float(x) * avg_tlc / 100) if pd.notnull(x) and x != "" else x
   )
   normalized_avg_data['Normalized Average Volume'] = norm_avg_vol
   ```

5. **Multi-Sheet Output**:
   - Creates five separate sheets in the Excel file:
     1. Raw Data
     2. Individual Data (% TLC)
     3. Averages
     4. Absolute Volume Data
     5. Normalized Average Data
   - Adds explanatory notes to each sheet

---

## Technical Implementation Details

### UI Architecture

The application uses a modular UI architecture with three main interfaces:

1. **Main Application**: Acts as a launcher and navigation hub
   - Creates a main window with buttons to launch each tool
   - Handles user navigation between tools

2. **Tool Interfaces**: Each tool has a dedicated interface
   - Implemented as modal windows (tkinter Toplevel)
   - Runs operations in separate threads to keep UI responsive
   - Reports status and results back to the user

3. **Dialog Boxes**: Used for specific data entry tasks
   - TLC value entry dialog
   - Subject ID entry dialog
   - File selection dialogs

### Multithreading Implementation

Long-running operations are executed in separate threads to prevent UI freezing:

```python
def start_processing(self):
    # Start processing in a separate thread
    self.status_var.set("Processing...")
    thread = threading.Thread(
        target=self.run_processing_thread,
        args=(self.selected_files, self.tlc_values, ...)
    )
    thread.daemon = True
    thread.start()
```

Results are safely returned to the UI thread using Tkinter's `after` method:

```python
def run_processing_thread(self):
    try:
        # Process the file
        result = process_function(...)
        
        # Update UI safely
        self.window.after(0, lambda: self.processing_complete(result))
    except Exception as e:
        # Handle errors and update UI
        self.window.after(0, lambda: messagebox.showerror(...))
```

### Error Handling Approach

The application uses a comprehensive error handling approach:

1. **Function-Level Try/Except Blocks**:
   - Each major function has error handling
   - Returns success/failure flags with results

2. **Thread-Level Error Catching**:
   - Processing threads catch and report all exceptions
   - Prevents thread crashes from affecting UI

3. **User-Friendly Error Messages**:
   - Converts technical errors to user-friendly messages
   - Provides specific information about failed files

4. **Partial Success Handling**:
   - When processing multiple files, allows some to fail without aborting
   - Provides reports of which files succeeded and which failed

---

## Mathematical Equations and Algorithms

### TLC Percentage Conversion

1. **Volume to Percentage Conversion**:
   ```
   percent_of_TLC = (raw_volume / TLC_value) * 100
   ```

2. **Percentage to Absolute Conversion**:
   ```
   absolute_volume = (percent_of_TLC * average_TLC) / 100
   ```

### Flow-Volume Analysis Algorithms

1. **Zero Flow Point Interpolation**:
   ```
   interpolated_time = t1 + ((0 - f1) / ((f2 - f1) / (t2 - t1)))
   ```
   Where:
   - t1, t2 are adjacent time points
   - f1, f2 are flow values at those time points
   - 0 is the target flow value (zero)

2. **Flow Interpolation at Volume Intervals**:
   ```
   Time_at_Volume_Interval = t1 + ((Actual_Volume_Interval - v1) / ((v2 - v1) / (t2 - t1)))
   Flow_at_Volume_Interval = f1 + ((f2 - f1) / (t2 - t1)) * (Time_at_Volume_Interval - t1)
   ```
   Where:
   - t1, t2 are adjacent time points
   - v1, v2 are volume values at those time points
   - f1, f2 are flow values at those time points
   - Actual_Volume_Interval is the target volume

3. **Standard Error Calculation**:
   ```
   SEM = numpy.std(values, ddof=1)
   ```
   Using n-1 degrees of freedom for unbiased estimation

---

## Data Structures and File Formats

### Input File Requirements

1. **Raw Respiratory Data**:
   - Excel file (.xlsx)
   - Contains markers "ltr/s" for flow data
   - Contains markers "ltr" for volume data

2. **Processed Data Files**:
   - Excel file (.xlsx)
   - Contains columns: Time, Vol, Flow
   - Optionally contains a sheet named "Avg Vol Bin Data"
   - Columns should contain keywords like "insp", "vol", "flow", "exp"

### Internal Data Structures

1. **Breath Data Dictionary**:
   - Organizes data by breath and phase
   - Example structure:
     ```
     {
       "Breath_0": {
         "Insp_Time": [...],
         "Insp_Vol": [...],
         "Insp_Flow": [...],
         "Exp_Time": [...],
         "Exp_Vol": [...],
         "Exp_Flow": [...]
       },
       "Breath_1": {
         ...
       }
     }
     ```

2. **Time Bins Result Dictionary**:
   - Complex nested dictionary containing:
     - Breath-by-breath data
     - Averages and statistical measures
     - Original and normalized data
     - Metadata for processing

3. **Processed Files Dictionary**:
   - Maps file paths to processed data:
     ```
     {
       "file_path_1": {
         "insp_vol": Series(...),
         "insp_flow": Series(...),
         "exp_vol": Series(...),
         "exp_flow": Series(...),
         "raw_insp_vol": Series(...),
         "raw_exp_vol": Series(...),
         "tlc": 6.2,
         "subject_id": "Patient1",
         "filename": "data1.xlsx"
       },
       "file_path_2": {
         ...
       }
     }
     ```

### Output File Format

The horizontal layout output creates an Excel file with five sheets:

1. **Raw Data**: Original flow and volume values
2. **Individual Data**: Volume as % of TLC and flow 
3. **Averages**: Average % TLC and flow values
4. **Absolute Volume Data**: Converted back to absolute volume
5. **Normalized Average Data**: Average data in absolute terms

---

## Configuration Settings

The application uses a central configuration file (`config.py`) with these key settings:

```python
# Application settings
APP_TITLE = "Respiratory Analysis Toolkit"
APP_WIDTH = 650
APP_HEIGHT = 600

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
```

These settings control:
- Application appearance and dimensions
- File type filters and extensions
- Pattern matching for column identification
- Default worksheet names
- Output format options
- UI messages

---

## Troubleshooting and FAQ

### Common Issues

1. **Column Identification Failures**:
   - Problem: Software can't find required data columns
   - Technical cause: Pattern matching fails to identify columns
   - Solution: Ensure column names contain the required patterns (e.g., "insp vol", "exp flow")

2. **Zero Flow Point Detection Issues**:
   - Problem: Breath detection is incorrect or missing breaths
   - Technical cause: Algorithm sensitivity to noise or irregular breathing
   - Solution: Pre-process data to smooth irregularities

3. **TLC Conversion Errors**:
   - Problem: "Division by zero" or invalid TLC values
   - Technical cause: Invalid TLC values (zero or negative)
   - Solution: Ensure positive TLC values for all files

### Frequently Asked Questions

1. **Q: Why do some files fail to process?**
   - A: Files fail when required columns can't be found or when data format is incompatible. Check column naming and sheet structure.

2. **Q: How are breaths identified in the Flow-Volume Averaging tool?**
   - A: Breaths are identified by detecting zero-flow crossing points with validation to ensure they represent actual breath transitions, not noise.

3. **Q: What's the difference between time-bin and volume-bin methods?**
   - A: 
     - Time-bin: Divides each breath into equal time intervals
     - Volume-bin: Divides each breath into equal volume intervals
     - These provide complementary perspectives on breathing patterns

4. **Q: How is the normalized average data calculated?**
   - A: It takes the average volume (% of TLC) and converts it back to absolute volume using the average TLC across all files: normalized_volume = (percent * avg_TLC) / 100

---

## Technical Contributors

This software was developed to support respiratory research and clinical analysis, with contributions from medical and technical experts. The current version includes three integrated tools to form a complete respiratory data analysis workflow.

For technical support or questions about the internal algorithms and calculations, please refer to this documentation or contact the development team.