"""
UI Callbacks for DSSAT Viewer (Tkinter Version)
"""
import sys
import os
import threading
import traceback
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from matplotlib.collections import PathCollection

# Add project root to Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Import project modules
import config
from utils.dssat_paths import get_crop_details, prepare_folders
from data.dssat_io import (
    prepare_experiment, prepare_treatment, prepare_out_files, 
    read_file, read_observed_data, read_evaluate_file,
    create_batch_file, run_treatment
)
from data.data_processing import (
    handle_missing_xvar, get_variable_info, improved_smart_scale,
    get_evaluate_variable_pairs, get_all_evaluate_variables,
    unified_date_convert
)
from models.metrics import MetricsCalculator

logger = logging.getLogger(__name__)

class DSSATCallbacks:
    """Class to handle all UI callbacks for the DSSAT Viewer application.
    
    This class is responsible for connecting UI elements to their respective
    actions and data processing functions.
    
    Attributes:
        app (DSSATViewer): Reference to the main application instance
        widgets (dict): Reference to the application's UI widgets
        data (dict): Dictionary to store data used by callbacks
    """
    
    def __init__(self, app):
        """Initialize the callbacks handler.
        
        Args:
            app (DSSATViewer): Reference to the main application instance
        """
        self.app = app
        self.widgets = app.widgets
        
        # Store data used by callbacks
        self.data = {
            'execution_completed': False,
            'treatments': [],
            'treatment_options': {},
            'simulation_data': None,
            'observed_data': None,
            'evaluate_data': None,
            'scaling_factors': {}
        }
        
        # Register callbacks
        self.register_callbacks()
        
        # Initialize UI elements
        self.initialize_ui()
    
    def register_callbacks(self):
        """Register callbacks for UI elements."""
        # Folder selector
        self.widgets['folder_combo'].bind('<<ComboboxSelected>>', self.on_folder_selected)
        
        # Experiment selector
        self.widgets['experiment_combo'].bind('<<ComboboxSelected>>', self.on_experiment_selected)
        
        # Run button
        self.widgets['run_button'].config(command=self.on_run_button_clicked)
        
        # Output file selector
        self.widgets['output_listbox'].bind('<<ListboxSelect>>', self.on_output_files_selected)
        
        # X variable selector
        self.widgets['x_combo'].bind('<<ComboboxSelected>>', self.on_variable_selected)
        
        # Y variable selector - using listbox for multiple selection
        self.widgets['y_listbox'].bind('<<ListboxSelect>>', self.on_variable_selected)
        
        # Refresh button
        self.widgets['refresh_button'].config(command=self.on_refresh_button_clicked)
        
        # Notebook tab change
        self.widgets['notebook'].bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def initialize_ui(self):
        """Initialize UI elements with data."""
        # Initialize folder selector
        folders = prepare_folders()
        if folders:
            self.widgets['folder_combo']['values'] = folders
            self.widgets['folder_combo'].current(0)
            self.on_folder_selected(None)  # Trigger folder selection callback
    
    def update_status(self, message):
        """Update status bar with a message.
        
        Args:
            message (str): Message to display
        """
        self.widgets['status_var'].set(message)
        self.app.root.update_idletasks()
    
    def show_progress(self, visible=True):
        """Show or hide progress bar.
        
        Args:
            visible (bool): Whether to show or hide progress bar
        """
        if visible:
            self.widgets['progress_bar'].pack(side=tk.RIGHT, padx=5)
            self.widgets['progress_var'].set(0)
        else:
            self.widgets['progress_bar'].pack_forget()
    
    def update_progress(self, value):
        """Update progress bar value.
        
        Args:
            value (float): Progress value between 0 and 100
        """
        self.widgets['progress_var'].set(value)
        self.app.root.update_idletasks()
    
    def on_folder_selected(self, event):
        """Handle folder selection.
        
        Args:
            event: ComboboxSelected event
        """
        selected_folder = self.widgets['folder_var'].get()
        if not selected_folder:
            return
        
        self.update_status(f"Loading experiments for {selected_folder}...")
        
        try:
            # Reset execution state
            self.data['execution_completed'] = False
            
            # Get experiments for selected folder
            experiments = prepare_experiment(selected_folder)
            
            # Clear experiment combobox and update with new values
            self.widgets['experiment_combo']['values'] = [filename for _, filename in experiments]
            if experiments:
                self.widgets['experiment_var'].set(experiments[0][1])  # Set to first experiment
                
                # Update treatments
                self.on_experiment_selected(None)
            else:
                self.widgets['experiment_var'].set('')
                self.widgets['treatment_listbox'].delete(0, tk.END)
            
            # Hide output files frame
            self.widgets['output_frame'].grid_remove()
            self.widgets['variables_frame'].grid_remove()
            
            self.update_status("Ready")
            
        except Exception as e:
            logger.error(f"Error loading experiments: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error loading experiments: {str(e)}")
            self.update_status("Error loading experiments")
    
    def on_experiment_selected(self, event):
        """Handle experiment selection.
        
        Args:
            event: ComboboxSelected event
        """
        selected_folder = self.widgets['folder_var'].get()
        selected_experiment = self.widgets['experiment_var'].get()
        
        if not selected_folder or not selected_experiment:
            return
        
        self.update_status(f"Loading treatments for {selected_experiment}...")
        
        try:
            # Reset execution state
            self.data['execution_completed'] = False
            
            # Clear treatment listbox
            self.widgets['treatment_listbox'].delete(0, tk.END)
            
            # Get treatments for selected experiment
            treatments = prepare_treatment(selected_folder, selected_experiment)
            if treatments is not None and not treatments.empty:
                treatments["TR"] = treatments["TR"].astype(str)
                
                # Store treatment options for later use
                self.data['treatment_options'] = {}
                
                # Add treatments to listbox
                for i, (_, row) in enumerate(treatments.iterrows()):
                    item_text = f"{row.TR} - {row.TNAME}"
                    self.widgets['treatment_listbox'].insert(tk.END, item_text)
                    
                    # Store treatment option for reference
                    self.data['treatment_options'][row.TR] = item_text
                
                # Select all treatments by default
                for i in range(self.widgets['treatment_listbox'].size()):
                    self.widgets['treatment_listbox'].selection_set(i)
            
            # Hide output files frame
            self.widgets['output_frame'].grid_remove()
            self.widgets['variables_frame'].grid_remove()
            
            self.update_status("Ready")
            
        except Exception as e:
            logger.error(f"Error loading treatments: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error loading treatments: {str(e)}")
            self.update_status("Error loading treatments")
    
    def get_selected_treatments(self):
        """Get selected treatments from listbox.
        
        Returns:
            list: List of selected treatment numbers
        """
        selected_indices = self.widgets['treatment_listbox'].curselection()
        selected_treatments = []
        
        for i in selected_indices:
            item_text = self.widgets['treatment_listbox'].get(i)
            treatment_num = item_text.split(' - ')[0]
            selected_treatments.append(treatment_num)
        
        return selected_treatments
    
    def on_run_button_clicked(self):
        """Handle run button click."""
        selected_folder = self.widgets['folder_var'].get()
        selected_experiment = self.widgets['experiment_var'].get()
        selected_treatments = self.get_selected_treatments()
        
        if not selected_folder or not selected_experiment or not selected_treatments:
            messagebox.showwarning("Warning", "Please select folder, experiment, and at least one treatment.")
            return
        
        self.update_status(f"Running treatments: {', '.join(selected_treatments)}...")
        self.show_progress(True)
        
        # Define the task to run in the background
        def run_task():
            try:
                # Update progress
                self.update_progress(10)
                
                # Create input data for treatment execution
                input_data = {
                    "folders": selected_folder,
                    "executables": config.DSSAT_EXE,
                    "experiment": selected_experiment,
                    "treatment": selected_treatments,
                }
                
                # Create batch file
                self.update_progress(30)
                batch_file_path = create_batch_file(input_data, config.DSSAT_BASE)
                
                # Run treatment
                self.update_progress(50)
                run_treatment(input_data, config.DSSAT_BASE)
                
                # Set execution completed flag
                self.data['execution_completed'] = True
                self.data['treatments'] = selected_treatments
                
                # Update output files
                self.update_progress(80)
                self.update_output_files()
                
                # Update progress
                self.update_progress(100)
                
                return "Treatment execution completed successfully."
                
            except Exception as e:
                logger.error(f"Error running treatment: {e}", exc_info=True)
                raise
        
        # Define success callback
        def on_success(result):
            self.show_progress(False)
            self.update_status("Treatment execution completed")
            messagebox.showinfo("Success", result)
            
            # Show output files frame
            self.widgets['output_frame'].grid()
        
        # Define error callback
        def on_error(error_msg):
            self.show_progress(False)
            self.update_status("Error running treatment")
            messagebox.showerror("Error", f"Error running treatment: {error_msg}")
        
        # Run the task in a separate thread
        self.app.run_long_task(run_task, success_callback=on_success, error_callback=on_error)
    
    def update_output_files(self):
        """Update output files listbox."""
        selected_folder = self.widgets['folder_var'].get()
        
        if not selected_folder:
            return
        
        try:
            # Clear output listbox
            self.widgets['output_listbox'].delete(0, tk.END)
            
            # Get output files
            out_files = prepare_out_files(selected_folder)
            
            if out_files:
                # Add output files to listbox
                for out_file in out_files:
                    self.widgets['output_listbox'].insert(tk.END, out_file)
                
                # Select PlantGro.OUT by default if available
                if "PlantGro.OUT" in out_files:
                    idx = out_files.index("PlantGro.OUT")
                    self.widgets['output_listbox'].selection_set(idx)
                else:
                    # Otherwise select first file
                    self.widgets['output_listbox'].selection_set(0)
                
                # Trigger selection event
                self.on_output_files_selected(None)
            
        except Exception as e:
            logger.error(f"Error updating output files: {e}", exc_info=True)
    
    def on_output_files_selected(self, event):
        """Handle output files selection.
        
        Args:
            event: ListboxSelect event
        """
        if not self.data['execution_completed']:
            return
        
        selected_indices = self.widgets['output_listbox'].curselection()
        if not selected_indices:
            return
        
        selected_files = [self.widgets['output_listbox'].get(i) for i in selected_indices]
        selected_folder = self.widgets['folder_var'].get()
        
        self.update_status(f"Loading variables from {', '.join(selected_files)}...")
        
        try:
            # Update variables
            self.update_variables(selected_folder, selected_files)
            
            # Show variables frame
            self.widgets['variables_frame'].grid()
            
            self.update_status("Ready")
            
        except Exception as e:
            logger.error(f"Error loading variables: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error loading variables: {str(e)}")
            self.update_status("Error loading variables")
    
    def update_variables(self, selected_folder, selected_out_files):
        """Update variable selectors based on selected OUT files.
        
        Args:
            selected_folder (str): Selected folder
            selected_out_files (list): Selected output files
        """
        if not selected_folder or not selected_out_files:
            return
        
        try:
            # Get crop directory
            crop_details = get_crop_details()
            crop_info = next(
                (crop for crop in crop_details 
                if crop['name'].upper() == selected_folder.upper()),
                None
            )
            
            if not crop_info:
                logger.error(f"Could not find crop info for: {selected_folder}")
                return

            # Collect columns from all selected files
            all_columns = set()
            for out_file in selected_out_files:
                file_path = os.path.join(crop_info['directory'], out_file)
                logger.info(f"Reading file: {file_path}")
                
                data = read_file(file_path)
                if data is not None and not data.empty:
                    all_columns.update(
                        col for col in data.columns 
                        if col not in ["TRT", "FILEX"]
                    )

            # Create variable options with labels
            var_options = []
            for col in sorted(all_columns):
                var_label, description = get_variable_info(col)
                display_name = var_label if var_label else col
                var_options.append((col, display_name))
            
            # Update X variable combobox
            self.widgets['x_combo']['values'] = [display_name for _, display_name in var_options]
            
            # Set default values
            default_x_index = -1
            if "DATE" in all_columns:
                for i, (col, _) in enumerate(var_options):
                    if col == "DATE":
                        default_x_index = i
                        break
            
            if default_x_index >= 0:
                self.widgets['x_combo'].current(default_x_index)
            elif var_options:
                self.widgets['x_combo'].current(0)
            
            # Update Y variable listbox
            self.widgets['y_listbox'].delete(0, tk.END)
            for col, display_name in var_options:
                self.widgets['y_listbox'].insert(tk.END, f"{display_name} ({col})")
            
            # Select default Y variable
            if "CWAD" in all_columns:
                for i, (col, _) in enumerate(var_options):
                    if col == "CWAD":
                        self.widgets['y_listbox'].selection_set(i)
                        break
            elif var_options:
                self.widgets['y_listbox'].selection_set(0)
            
            # Store variable options for reference
            self.data['variable_options'] = var_options
            
        except Exception as e:
            logger.error(f"Error updating variables: {e}", exc_info=True)
            raise
    
    def on_variable_selected(self, event):
        """Handle variable selection.
        
        Args:
            event: ComboboxSelected or ListboxSelect event
        """
        # Do nothing, wait for refresh button
        pass
    
    def get_selected_y_variables(self):
        """Get selected Y variables from listbox.
        
        Returns:
            list: List of selected Y variable codes
        """
        selected_indices = self.widgets['y_listbox'].curselection()
        selected_vars = []
        
        for i in selected_indices:
            item_text = self.widgets['y_listbox'].get(i)
            # Extract variable code from the text "Display Name (CODE)"
            var_code = item_text.split("(")[-1].strip(")")
            selected_vars.append(var_code)
        
        return selected_vars
    
    def on_refresh_button_clicked(self):
        """Handle refresh button click."""
        if not self.data['execution_completed']:
            messagebox.showwarning("Warning", "Please run a treatment first.")
            return
        
        selected_folder = self.widgets['folder_var'].get()
        selected_experiment = self.widgets['experiment_var'].get()
        selected_treatments = self.data['treatments']
        selected_out_files = [self.widgets['output_listbox'].get(i) 
                             for i in self.widgets['output_listbox'].curselection()]
        
        x_var_display = self.widgets['x_var'].get()
        x_var = None
        for code, display in self.data['variable_options']:
            if display == x_var_display:
                x_var = code
                break
        
        y_vars = self.get_selected_y_variables()
        
        if not (selected_folder and selected_experiment and selected_treatments and 
                selected_out_files and x_var and y_vars):
            messagebox.showwarning("Warning", "Please select all required options.")
            return
        
        self.update_status("Refreshing plot...")
        self.show_progress(True)
        
        # Define the task to run in the background
        def refresh_task():
            try:
                # Update progress
                self.update_progress(10)
                
                # Read data from output files
                all_data = []
                for selected_out_file in selected_out_files:
                    file_path = os.path.join(
                        config.DSSAT_BASE, selected_folder, selected_out_file
                    )
                    sim_data = read_file(file_path)
                    if sim_data is None or sim_data.empty:
                        continue
                        
                    sim_data.columns = sim_data.columns.str.strip().str.upper()
                    
                    if "TRNO" in sim_data.columns and "TRT" not in sim_data.columns:
                        sim_data["TRT"] = sim_data["TRNO"]
                    elif "TRT" not in sim_data.columns:
                        sim_data["TRT"] = "1"
                        
                    sim_data["TRT"] = sim_data["TRT"].astype(str)
                    
                    for col in ["YEAR", "DOY"]:
                        if col in sim_data.columns:
                            sim_data[col] = (
                                pd.to_numeric(sim_data[col], errors="coerce")
                                .fillna(0)
                                .replace([np.inf, -np.inf], 0)
                            )
                        else:
                            sim_data[col] = 0
                            
                    sim_data["DATE"] = sim_data.apply(
                        lambda row: unified_date_convert(row["YEAR"], row["DOY"]),
                        axis=1,
                    )
                    sim_data["DATE"] = sim_data["DATE"].dt.strftime("%Y-%m-%d")
                    sim_data["source"] = "sim"
                    sim_data["FILE"] = selected_out_file
                    all_data.append(sim_data)
                
                self.update_progress(40)
                
                if not all_data:
                    raise ValueError("No data found in selected output files.")
                    
                sim_data = pd.concat(all_data, ignore_index=True)
                missing_values = {-99, -99.0, -99.9, -99.99}
                
                # Read observed data
                obs_data = None
                if selected_experiment:
                    obs_data = read_observed_data(
                        selected_folder, selected_experiment, x_var, y_vars
                    )
                    if obs_data is not None and not obs_data.empty:
                        obs_data["source"] = "obs"
                        obs_data = handle_missing_xvar(obs_data, x_var, sim_data)
                        
                        if obs_data is not None:
                            if "TRNO" in obs_data.columns:
                                obs_data["TRNO"] = obs_data["TRNO"].astype(str)
                                obs_data = obs_data.rename(columns={"TRNO": "TRT"})
                                
                            for var in y_vars:
                                if var in obs_data.columns:
                                    obs_data[var] = pd.to_numeric(
                                        obs_data[var], errors="coerce"
                                    )
                                    obs_data.loc[
                                        obs_data[var].isin(missing_values), var
                                    ] = np.nan
                
                self.update_progress(60)
                
                # Store data for reference
                self.data['simulation_data'] = sim_data
                self.data['observed_data'] = obs_data
                
                # Calculate metrics
                metrics_data = self.calculate_metrics(sim_data, obs_data, y_vars, selected_treatments)
                
                # Update progress
                self.update_progress(80)
                
                # Update plots
                self.update_plots(sim_data, obs_data, x_var, y_vars, selected_treatments)
                
                # Update data preview
                self.update_data_preview(sim_data, obs_data)
                
                # Update metrics display
                self.update_metrics_display(metrics_data)
                
                # Update progress
                self.update_progress(100)
                
                return "Plot refreshed successfully."
                
            except Exception as e:
                logger.error(f"Error refreshing plot: {e}", exc_info=True)
                raise
        
        # Define success callback
        def on_success(result):
            self.show_progress(False)
            self.update_status("Plot refreshed")
        
        # Define error callback
        def on_error(error_msg):
            self.show_progress(False)
            self.update_status("Error refreshing plot")
            messagebox.showerror("Error", f"Error refreshing plot: {error_msg}")
        
        # Run the task in a separate thread
        self.app.run_long_task(refresh_task, success_callback=on_success, error_callback=on_error)
    
    def calculate_metrics(self, sim_data, obs_data, y_vars, selected_treatments):
        """Calculate performance metrics.
        
        Args:
            sim_data (pd.DataFrame): Simulation data
            obs_data (pd.DataFrame): Observed data
            y_vars (list): Y variables to calculate metrics for
            selected_treatments (list): Selected treatments
            
        Returns:
            list: List of metric dictionaries
        """
        if obs_data is None or obs_data.empty:
            return []
        
        metrics_data = []
        
        for selected_out_file in sim_data["FILE"].unique():
            file_sim_data = sim_data[sim_data["FILE"] == selected_out_file]
            
            unique_treatments_obs = obs_data["TRT"].unique()
            unique_treatments_sim = file_sim_data["TRT"].unique()
            common_treatments = set(unique_treatments_obs) & set(unique_treatments_sim)
            
            for var in y_vars:
                if var in obs_data.columns and var in file_sim_data.columns:
                    for treatment in common_treatments:
                        if treatment not in selected_treatments:
                            continue
                            
                        filtered_obs_data = obs_data[obs_data["TRT"] == treatment]
                        filtered_sim_data = file_sim_data[file_sim_data["TRT"] == treatment]
                        
                        if not filtered_obs_data.empty and not filtered_sim_data.empty:
                            common_dates = filtered_sim_data["DATE"].isin(filtered_obs_data["DATE"])
                            filtered_sim = filtered_sim_data[common_dates]
                            
                            # Combine data to align observations
                            combined = pd.merge(
                                filtered_sim[["DATE", var]],
                                filtered_obs_data[["DATE", var]],
                                on="DATE",
                                suffixes=('_sim', '_obs')
                            )
                            
                            sim_values = combined[f"{var}_sim"].to_numpy()
                            obs_values = combined[f"{var}_obs"].to_numpy()
                            
                            if len(obs_values) > 0 and len(sim_values) > 0:
                                var_metrics = MetricsCalculator.calculate_metrics(
                                    sim_values, obs_values, treatment
                                )
                                
                                if var_metrics is not None:
                                    treatment_name = self.data['treatment_options'].get(
                                        treatment, f"Treatment {treatment}"
                                    )
                                    var_label, _ = get_variable_info(var)
                                    display_name = var_label if var_label else var
                                    
                                    metrics_data.append({
                                        "Treatment": treatment_name,
                                        "Variable": display_name,
                                        "n": var_metrics["n"],
                                        "RMSE": var_metrics["RMSE"],
                                        "NRMSE": var_metrics["NRMSE"],
                                        "d-stat": var_metrics["Willmott's d-stat"]
                                    })
        
        return metrics_data
    
    def update_plots(self, sim_data, obs_data, x_var, y_vars, selected_treatments):
        """Update time series and scatter plots.
        
        Args:
            sim_data (pd.DataFrame): Simulation data
            obs_data (pd.DataFrame): Observed data
            x_var (str): X variable name
            y_vars (list): Y variables
            selected_treatments (list): Selected treatments
        """
        # Update time series plot
        self.update_time_series_plot(sim_data, obs_data, x_var, y_vars, selected_treatments)
        
        # Update scatter plot if needed
        current_tab = self.widgets['notebook'].index(self.widgets['notebook'].select())
        if current_tab == 1:  # Scatter Plot tab
            self.update_scatter_plot(sim_data, obs_data, y_vars, selected_treatments)
    
    def update_time_series_plot(self, sim_data, obs_data, x_var, y_vars, selected_treatments):
        """Update time series plot.
        
        Args:
            sim_data (pd.DataFrame): Simulation data
            obs_data (pd.DataFrame): Observed data
            x_var (str): X variable name
            y_vars (list): Y variables
            selected_treatments (list): Selected treatments
        """
        # Clear the figure
        fig = self.widgets['time_series_fig']
        fig.clear()
        
        # Create subplot
        ax = fig.add_subplot(111)
        
        # Define line styles, marker symbols, and colors
        line_styles = ['-', '--', '-.', ':']
        marker_symbols = ['o', 's', '^', 'D', '*']
        colors = plt.cm.tab10.colors
        
        # Get treatments for legend
        treatment_names = self.data['treatment_options']
        
        # Create scaling factors for y-axis normalization
        scaling_factors = {}
        for var in y_vars:
            if var in sim_data.columns:
                sim_values = pd.to_numeric(sim_data[var], errors="coerce").dropna().values
                if len(sim_values) > 0:
                    var_min, var_max = np.min(sim_values), np.max(sim_values)
                    
                    if np.isclose(var_min, var_max):
                        midpoint = (10000 + 1000) / 2
                        scaling_factors[var] = (1, midpoint)
                    else:
                        scale_factor = (10000 - 1000) / (var_max - var_min)
                        offset = 1000 - var_min * scale_factor
                        scaling_factors[var] = (scale_factor, offset)
        
        # Store scaling factors for reference
        self.data['scaling_factors'] = scaling_factors
        
        # Plot data
        for i, var in enumerate(y_vars):
            var_label, _ = get_variable_info(var)
            display_name = var_label if var_label else var
            
            for j, trt in enumerate(selected_treatments):
                # Plot simulated data
                sim_trt_data = sim_data[(sim_data["TRT"] == trt) & (sim_data[var].notna())]
                if not sim_trt_data.empty:
                    trt_name = treatment_names.get(trt, f"Treatment {trt}")
                    label = f"{display_name} (Sim) - {trt_name}"
                    
                    # Apply scaling
                    if var in scaling_factors:
                        scale_factor, offset = scaling_factors[var]
                        y_values = sim_trt_data[var] * scale_factor + offset
                    else:
                        y_values = sim_trt_data[var]
                    
                    ax.plot(
                        sim_trt_data[x_var], 
                        y_values,
                        linestyle=line_styles[i % len(line_styles)],
                        color=colors[j % len(colors)],
                        label=label
                    )
                
                # Plot observed data if available
                if obs_data is not None and not obs_data.empty:
                    obs_trt_data = obs_data[(obs_data["TRT"] == trt) & (obs_data[var].notna())]
                    if not obs_trt_data.empty:
                        trt_name = treatment_names.get(trt, f"Treatment {trt}")
                        label = f"{display_name} (Obs) - {trt_name}"
                        
                        # Apply scaling
                        if var in scaling_factors:
                            scale_factor, offset = scaling_factors[var]
                            y_values = obs_trt_data[var] * scale_factor + offset
                        else:
                            y_values = obs_trt_data[var]
                        
                        ax.scatter(
                            obs_trt_data[x_var],
                            y_values,
                            marker=marker_symbols[i % len(marker_symbols)],
                            color=colors[j % len(colors)],
                            label=label,
                            edgecolors='black',
                            s=50
                        )
        
        # Add scaling information
        scaling_text = []
        for var in y_vars:
            if var in scaling_factors:
                var_label, _ = get_variable_info(var)
                display_name = var_label if var_label else var
                scale_factor, offset = scaling_factors[var]
                scaling_text.append(f"{display_name} = {scale_factor:.6f} * {display_name} + {offset:.2f}")
        
        if scaling_text:
            fig.text(
                0.02, 0.02, 
                "Scaling Factors:\n" + "\n".join(scaling_text),
                fontsize=8,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
            )
        
        # Set title and labels
        x_var_label, _ = get_variable_info(x_var)
        x_display = x_var_label if x_var_label else x_var
        
        y_var_labels = []
        for var in y_vars:
            var_label, _ = get_variable_info(var)
            y_var_labels.append(var_label if var_label else var)
        
        ax.set_xlabel(x_display, fontsize=12)
        ax.set_ylabel(", ".join(y_var_labels), fontsize=12)
        ax.set_title("Time Series Plot", fontsize=14)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8)
        
        # Adjust layout
        fig.tight_layout()
        
        # Redraw canvas
        self.widgets['time_series_canvas'].draw()
    
    def update_scatter_plot(self, sim_data, obs_data, y_vars, selected_treatments):
        """Update scatter plot.
        
        Args:
            sim_data (pd.DataFrame): Simulation data
            obs_data (pd.DataFrame): Observed data
            y_vars (list): Y variables
            selected_treatments (list): Selected treatments
        """
        # If no observed data, nothing to plot
        if obs_data is None or obs_data.empty:
            fig = self.widgets['scatter_fig']
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No observed data available for scatter plot", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            fig.tight_layout()
            self.widgets['scatter_canvas'].draw()
            return
        
        # Get treatments for legend
        treatment_names = self.data['treatment_options']
        
        # Define colors and markers
        colors = plt.cm.tab10.colors
        marker_symbols = ['o', 's', '^', 'D', '*']
        
        # Create subplots - one for each variable
        fig = self.widgets['scatter_fig']
        fig.clear()
        
        n_vars = len(y_vars)
        if n_vars <= 3:
            # Use a single row
            n_rows, n_cols = 1, n_vars
        elif n_vars <= 6:
            # Use two rows
            n_rows, n_cols = 2, (n_vars + 1) // 2
        else:
            # Use three rows
            n_rows, n_cols = 3, (n_vars + 2) // 3
        
        # Create a 1:1 line range based on all data
        all_values = []
        for var in y_vars:
            if var in obs_data.columns and var in sim_data.columns:
                for trt in selected_treatments:
                    obs_trt_data = obs_data[(obs_data["TRT"] == trt) & (obs_data[var].notna())]
                    sim_trt_data = sim_data[(sim_data["TRT"] == trt) & (sim_data[var].notna())]
                    
                    if not obs_trt_data.empty and not sim_trt_data.empty:
                        # Get common dates
                        common_dates = sim_trt_data["DATE"].isin(obs_trt_data["DATE"])
                        filtered_sim = sim_trt_data[common_dates]
                        
                        # Combine data to align observations
                        combined = pd.merge(
                            filtered_sim[["DATE", var]],
                            obs_trt_data[["DATE", var]],
                            on="DATE",
                            suffixes=('_sim', '_obs')
                        )
                        
                        all_values.extend(combined[f"{var}_sim"].tolist())
                        all_values.extend(combined[f"{var}_obs"].tolist())
        
        if not all_values:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No matching observed and simulated data for scatter plot",
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            fig.tight_layout()
            self.widgets['scatter_canvas'].draw()
            return
        
        # Calculate overall min and max for 1:1 line
        overall_min = min(all_values)
        overall_max = max(all_values)
        
        # Add some padding
        padding = (overall_max - overall_min) * 0.1
        overall_min -= padding
        overall_max += padding
        
        # Plot each variable
        for i, var in enumerate(y_vars):
            if var in obs_data.columns and var in sim_data.columns:
                row = i // n_cols
                col = i % n_cols
                
                # Calculate subplot index (1-based)
                subplot_idx = row * n_cols + col + 1
                
                ax = fig.add_subplot(n_rows, n_cols, subplot_idx)
                
                # Add 1:1 line
                ax.plot([overall_min, overall_max], [overall_min, overall_max], 
                       'r--', linewidth=1, label='1:1 Line')
                
                # Get variable info
                var_label, _ = get_variable_info(var)
                display_name = var_label if var_label else var
                
                # Set axis labels
                ax.set_xlabel(f'Simulated {display_name}', fontsize=10)
                ax.set_ylabel(f'Observed {display_name}', fontsize=10)
                
                # Set title
                ax.set_title(display_name, fontsize=12)
                
                # Add grid
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Set equal aspect ratio and limits
                ax.set_aspect('equal')
                ax.set_xlim(overall_min, overall_max)
                ax.set_ylim(overall_min, overall_max)
                
                # Plot data points for each treatment
                for j, trt in enumerate(selected_treatments):
                    trt_color = colors[j % len(colors)]
                    trt_marker = marker_symbols[j % len(marker_symbols)]
                    
                    obs_trt_data = obs_data[(obs_data["TRT"] == trt) & (obs_data[var].notna())]
                    sim_trt_data = sim_data[(sim_data["TRT"] == trt) & (sim_data[var].notna())]
                    
                    if not obs_trt_data.empty and not sim_trt_data.empty:
                        # Get common dates
                        common_dates = sim_trt_data["DATE"].isin(obs_trt_data["DATE"])
                        filtered_sim = sim_trt_data[common_dates]
                        
                        # Combine data to align observations
                        combined = pd.merge(
                            filtered_sim[["DATE", var]],
                            obs_trt_data[["DATE", var]],
                            on="DATE",
                            suffixes=('_sim', '_obs')
                        )
                        
                        if not combined.empty:
                            # Plot scatter points
                            trt_name = treatment_names.get(trt, f"Treatment {trt}")
                            ax.scatter(
                                combined[f"{var}_sim"],
                                combined[f"{var}_obs"],
                                marker=trt_marker,
                                color=trt_color,
                                label=trt_name,
                                edgecolors='black',
                                s=50,
                                alpha=0.7
                            )
                
                # Add statistics
                if i == 0:  # Only add legend to first subplot
                    ax.legend(loc='upper left', fontsize=8)
        
        # Adjust layout
        fig.tight_layout()
        
        # Redraw canvas
        self.widgets['scatter_canvas'].draw()
    
    def update_data_preview(self, sim_data, obs_data):
        """Update data preview treeview.
        
        Args:
            sim_data (pd.DataFrame): Simulation data
            obs_data (pd.DataFrame): Observed data
        """
        # Combine simulation and observed data if available
        combined_data = sim_data.copy()
        if obs_data is not None and not obs_data.empty:
            common_columns = list(set(sim_data.columns) & set(obs_data.columns))
            combined_data = pd.concat([sim_data[common_columns], obs_data[common_columns]], ignore_index=True)
        
        # Clear existing data
        tree = self.widgets['data_tree']
        for item in tree.get_children():
            tree.delete(item)
        
        # Configure columns
        tree['columns'] = list(combined_data.columns)
        tree['show'] = 'headings'  # Hide the first column (ID)
        
        # Set column headings
        for col in combined_data.columns:
            tree.heading(col, text=col)
            
            # Set column width based on content
            max_width = max(
                len(str(col)),
                max([len(str(val)) for val in combined_data[col].dropna().head(100)], default=0)
            )
            tree.column(col, width=max(50, min(200, max_width * 10)))
        
        # Add data rows (limit to first 1000 rows for performance)
        display_data = combined_data.head(1000)
        for i, row in display_data.iterrows():
            values = [str(row[col]) for col in combined_data.columns]
            tree.insert('', 'end', text=str(i), values=values)
    
    def update_metrics_display(self, metrics_data):
        """Update metrics treeview.
        
        Args:
            metrics_data (list): List of metrics dictionaries
        """
        # Clear existing data
        tree = self.widgets['metrics_tree']
        for item in tree.get_children():
            tree.delete(item)
        
        if not metrics_data:
            # Configure with default columns
            tree['columns'] = ['Message']
            tree['show'] = 'headings'
            tree.heading('Message', text='Message')
            tree.column('Message', width=400)
            
            # Add message
            tree.insert('', 'end', values=["No metrics available. Ensure observed data exists for comparison."])
            return
        
        # Get column names from first metrics dictionary
        columns = list(metrics_data[0].keys())
        
        # Configure columns
        tree['columns'] = columns
        tree['show'] = 'headings'
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            
            # Set column width based on content
            max_width = max(
                len(str(col)),
                max([len(str(metrics[col])) for metrics in metrics_data], default=0)
            )
            tree.column(col, width=max(80, min(200, max_width * 10)))
        
        # Add data rows
        for metrics in metrics_data:
            values = [str(metrics[col]) for col in columns]
            tree.insert('', 'end', values=values)
    
    def on_tab_changed(self, event):
        """Handle tab change event.
        
        Args:
            event: NotebookTabChanged event
        """
        # Get current tab
        current_tab = self.widgets['notebook'].index(self.widgets['notebook'].select())
        
        # If switching to Scatter Plot tab, update scatter plot
        if current_tab == 1 and self.data['execution_completed']:
            sim_data = self.data.get('simulation_data')
            obs_data = self.data.get('observed_data')
            
            if sim_data is not None:
                # Get Y variables
                y_vars = self.get_selected_y_variables()
                
                # Update scatter plot
                self.update_scatter_plot(sim_data, obs_data, y_vars, self.data['treatments'])