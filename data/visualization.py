"""
Visualization functions for DSSAT output data (Tkinter/Matplotlib version)
"""
import matplotlib.pyplot as plt
import numpy as np
import logging
import pandas as pd
from typing import List, Dict, Tuple, Union, Optional

logger = logging.getLogger(__name__)

def create_figure(data: pd.DataFrame, x_var: str, y_var: Union[str, List[str]], 
                 treatments: List[str], figsize=(10, 6)) -> Tuple[plt.Figure, plt.Axes]:
    """Create matplotlib figure with simulated and observed data.
    
    Args:
        data (pd.DataFrame): DataFrame containing simulation data
        x_var (str): X-axis variable
        y_var (Union[str, List[str]]): Y-axis variable(s)
        treatments (List[str]): List of treatment IDs to include
        figsize (tuple, optional): Figure size (width, height). Defaults to (10, 6).
        
    Returns:
        Tuple[plt.Figure, plt.Axes]: Matplotlib figure and axes objects
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if not (x_var and y_var) or data.empty:
        return fig, ax
        
    try:
        y_vars = y_var if isinstance(y_var, list) else [y_var]
        
        # Use different line styles for different variables
        line_styles = ['-', '--', '-.', ':']
        # Use different markers for observed data
        markers = ['o', 's', '^', 'D', '*']
        # Use different colors for different treatments
        colors = plt.cm.tab10.colors
        
        for i, trt in enumerate(treatments):
            treatment_data = data[data["TRT"] == trt]
            if treatment_data.empty:
                logger.warning(f"No data for treatment: {trt}")
                continue
                
            for j, y_var_item in enumerate(y_vars):
                # Get observed data flag if present
                is_observed = 'source' in treatment_data.columns and treatment_data['source'].iloc[0] == 'obs'
                
                # Plot data if variable exists in the dataset
                if y_var_item in treatment_data.columns:
                    valid_data = treatment_data[treatment_data[y_var_item].notna()]
                    
                    if valid_data.empty:
                        continue
                    
                    # Choose line style, marker and color
                    line_style = line_styles[j % len(line_styles)]
                    marker = markers[j % len(markers)] if is_observed else None
                    color = colors[i % len(colors)]
                    
                    label = f"{y_var_item} ({'Observed' if is_observed else 'Simulated'}, TRT {trt})"
                    
                    if is_observed:
                        # For observed data, use scatter plot
                        ax.scatter(
                            valid_data[x_var],
                            valid_data[y_var_item],
                            marker=marker,
                            color=color,
                            s=50,
                            label=label,
                            edgecolors='black'
                        )
                    else:
                        # For simulated data, use line plot
                        ax.plot(
                            valid_data[x_var],
                            valid_data[y_var_item],
                            linestyle=line_style,
                            color=color,
                            label=label,
                            marker='.',
                            markersize=4
                        )
        
        # Set labels and grid
        ax.set_xlabel(x_var)
        ax.set_ylabel(", ".join(y_vars))
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9)
        
        # Adjust layout
        fig.tight_layout()
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}")
        
    return fig, ax

def create_scatter_plot(sim_values: np.ndarray, obs_values: np.ndarray, 
                        variable_name: str, treatment: str, figsize=(8, 8)) -> Tuple[plt.Figure, plt.Axes]:
    """Create a scatter plot comparing simulated vs observed values.
    
    Args:
        sim_values (np.ndarray): Simulated values
        obs_values (np.ndarray): Observed values
        variable_name (str): Variable name for labels
        treatment (str): Treatment ID
        figsize (tuple, optional): Figure size. Defaults to (8, 8).
        
    Returns:
        Tuple[plt.Figure, plt.Axes]: Matplotlib figure and axes objects
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    try:
        # Filter out any NaN values
        mask = ~np.isnan(sim_values) & ~np.isnan(obs_values)
        sim_values = sim_values[mask]
        obs_values = obs_values[mask]
        
        if len(sim_values) == 0 or len(obs_values) == 0:
            logger.warning("No valid data points for scatter plot")
            return fig, ax
        
        # Determine axis limits based on min/max of both datasets
        min_val = min(np.min(sim_values), np.min(obs_values))
        max_val = max(np.max(sim_values), np.max(obs_values))
        
        # Add some padding
        padding = (max_val - min_val) * 0.1
        min_val -= padding
        max_val += padding
        
        # Plot 1:1 line
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='1:1 Line')
        
        # Plot scatter points
        ax.scatter(
            sim_values, 
            obs_values, 
            s=50, 
            color='blue', 
            edgecolors='black', 
            alpha=0.7,
            label=f'Treatment {treatment}'
        )
        
        # Calculate stats
        n = len(sim_values)
        from sklearn.metrics import mean_squared_error, r2_score
        from models.metrics import MetricsCalculator
        
        rmse = np.sqrt(mean_squared_error(obs_values, sim_values))
        r2 = r2_score(obs_values, sim_values)
        d_stat = MetricsCalculator.d_stat(obs_values, sim_values)
        
        # Add stats text
        stats_text = (
            f'n = {n}\n'
            f'RMSE = {rmse:.3f}\n'
            f'R² = {r2:.3f}\n'
            f'd-stat = {d_stat:.3f}'
        )
        
        ax.text(
            0.05, 0.95, stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        # Set labels and title
        ax.set_xlabel(f'Simulated {variable_name}')
        ax.set_ylabel(f'Observed {variable_name}')
        ax.set_title(f'{variable_name} - Treatment {treatment}')
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Set axis limits
        ax.set_xlim(min_val, max_val)
        ax.set_ylim(min_val, max_val)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Add legend
        ax.legend(loc='upper left')
        
        # Adjust layout
        fig.tight_layout()
        
    except Exception as e:
        logger.error(f"Error creating scatter plot: {str(e)}")
        
    return fig, ax

def create_multi_scatter_plot(sim_obs_data: Dict[str, Tuple[np.ndarray, np.ndarray]], 
                             figsize=(12, 10)) -> plt.Figure:
    """Create multiple scatter plots for different variables.
    
    Args:
        sim_obs_data (Dict[str, Tuple[np.ndarray, np.ndarray]]): 
            Dictionary mapping variable names to (sim_values, obs_values) tuples
        figsize (tuple, optional): Figure size. Defaults to (12, 10).
        
    Returns:
        plt.Figure: Matplotlib figure with subplots
    """
    n_vars = len(sim_obs_data)
    
    # Determine grid layout
    if n_vars <= 3:
        n_rows, n_cols = 1, n_vars
    elif n_vars <= 6:
        n_rows, n_cols = 2, (n_vars + 1) // 2
    else:
        n_rows, n_cols = 3, (n_vars + 2) // 3
    
    # Create figure and subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    
    try:
        # Flatten axes array for easier iteration if multiple subplots
        if n_vars > 1:
            axes = axes.flatten()
        else:
            axes = [axes]
        
        # Get global min/max for consistent 1:1 lines
        all_values = []
        for var_name, (sim_values, obs_values) in sim_obs_data.items():
            mask = ~np.isnan(sim_values) & ~np.isnan(obs_values)
            all_values.extend(sim_values[mask])
            all_values.extend(obs_values[mask])
        
        min_val = min(all_values) if all_values else 0
        max_val = max(all_values) if all_values else 1
        
        # Add padding
        padding = (max_val - min_val) * 0.1
        min_val -= padding
        max_val += padding
        
        # Plot each variable
        for i, (var_name, (sim_values, obs_values)) in enumerate(sim_obs_data.items()):
            if i >= len(axes):
                logger.warning(f"Not enough subplots for variable {var_name}")
                continue
            
            ax = axes[i]
            
            # Filter NaN values
            mask = ~np.isnan(sim_values) & ~np.isnan(obs_values)
            sim_filtered = sim_values[mask]
            obs_filtered = obs_values[mask]
            
            # Plot 1:1 line
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='1:1 Line')
            
            # Plot scatter points if we have data
            if len(sim_filtered) > 0:
                ax.scatter(
                    sim_filtered, 
                    obs_filtered, 
                    s=50, 
                    color='blue', 
                    edgecolors='black', 
                    alpha=0.7
                )
                
                # Calculate stats
                n = len(sim_filtered)
                from sklearn.metrics import mean_squared_error, r2_score
                from models.metrics import MetricsCalculator
                
                rmse = np.sqrt(mean_squared_error(obs_filtered, sim_filtered))
                r2 = r2_score(obs_filtered, sim_filtered)
                d_stat = MetricsCalculator.d_stat(obs_filtered, sim_filtered)
                
                # Add stats text
                stats_text = (
                    f'n = {n}\n'
                    f'RMSE = {rmse:.3f}\n'
                    f'R² = {r2:.3f}\n'
                    f'd-stat = {d_stat:.3f}'
                )
                
                ax.text(
                    0.05, 0.95, stats_text,
                    transform=ax.transAxes,
                    verticalalignment='top',
                    horizontalalignment='left',
                    fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
                )
            
            # Set labels
            ax.set_xlabel('Simulated', fontsize=9)
            ax.set_ylabel('Observed', fontsize=9)
            ax.set_title(var_name, fontsize=10)
            
            # Set equal aspect ratio
            ax.set_aspect('equal')
            
            # Set axis limits
            ax.set_xlim(min_val, max_val)
            ax.set_ylim(min_val, max_val)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.3)
        
        # Hide unused subplots
        for i in range(len(sim_obs_data), len(axes)):
            axes[i].axis('off')
        
        # Adjust layout
        fig.tight_layout()
        
    except Exception as e:
        logger.error(f"Error creating multi scatter plot: {str(e)}")
        
    return fig