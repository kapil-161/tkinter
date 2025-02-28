import sys
import os

# Add project root to Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

"""
Optimized data processing functions for DSSAT output
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import config

logger = logging.getLogger(__name__)

def standardize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimized data type standardization."""
    if df is None or df.empty:
        return df
        
    df = df.copy()
    
    # Remove all-NaN columns efficiently
    df = df.dropna(axis=1, how='all')
    
    # Define column types
    timestamp_cols = {"YEAR", "DOY", "DATE"}
    treatment_cols = {"TRT"}
    
    # Process columns by type
    for col in df.columns:
        if col in timestamp_cols or col in treatment_cols:
            df[col] = df[col].astype(str)
        else:
            # Try numeric conversion
            try:
                numeric_series = pd.to_numeric(df[col], errors="coerce")
                nan_ratio = numeric_series.isna().mean()
                
                if nan_ratio < 0.1:
                    df[col] = numeric_series.astype(
                        "Int64" if numeric_series.dropna().apply(lambda x: x.is_integer()).all()
                        else "float64"
                    )
            except Exception:
                pass
                
    return df

def unified_date_convert(year=None, doy=None, date_str=None):
    """Convert various date formats to datetime"""
    try:
        if date_str is not None:
            date_str = str(date_str).strip()
            if len(date_str) == 5 and date_str.isdigit():
                year_part = int(date_str[:2])
                doy_part = int(date_str[2:])
                century_prefix = "20" if year_part <= 30 else "19"
                full_year = century_prefix + f"{year_part:02d}"
                return pd.to_datetime(f"{full_year}{doy_part:03d}", format="%Y%j")
            else:
                logger.info(f"Invalid date_str format: {date_str}")
                return pd.NaT

        if year is not None and doy is not None:
            year = int(float(year))
            doy = int(float(doy))
            if 1 <= doy <= 366:
                return pd.to_datetime(f"{year}{doy:03d}", format="%Y%j")
            logger.info(f"Invalid DOY: {doy}")
            return pd.NaT

        return pd.NaT

    except Exception as e:
        logger.info(f"Error converting date: year={year}, doy={doy}, date_str={date_str}, error={e}")
        return pd.NaT

def handle_missing_xvar(obs_data: pd.DataFrame, x_var: str, sim_data: pd.DataFrame) -> pd.DataFrame:
    """Handle missing X variables in observed data"""
    if obs_data is None or obs_data.empty:
        return obs_data
        
    obs_data = obs_data.copy()
    
    # Handle DATE column
    if "DATE" in obs_data.columns:
        obs_data["DATE"] = pd.to_datetime(obs_data["DATE"], errors="coerce")
    if sim_data is not None and "DATE" in sim_data.columns:
        sim_data["DATE"] = pd.to_datetime(sim_data["DATE"], errors="coerce")
        
    # Check if x_var already exists
    if f"{x_var}" in obs_data.columns:
        return obs_data
    if x_var in obs_data.columns:
        obs_data[f"{x_var}"] = obs_data[x_var]
        return obs_data
        
    # Handle special variables
    if x_var.upper() in ["DAP", "DOY", "DAS"]:
        if "DATE" in obs_data.columns:
            if x_var.upper() == "DOY":
                obs_data[f"{x_var}"] = obs_data["DATE"].dt.dayofyear
            elif x_var.upper() in ["DAP", "DAS"]:
                start_date = pd.to_datetime(sim_data["DATE"]).min() if sim_data is not None else obs_data["DATE"].min()
                obs_data[f"{x_var}"] = (obs_data["DATE"] - start_date).dt.days
        else:
            logger.warning(f"Cannot create {x_var} without 'DATE' column in observed data")
            return obs_data
            
    # Try to infer from simulation data
    elif sim_data is not None and not sim_data.empty:
        if "DATE" in sim_data.columns:
            sim_dates = pd.to_datetime(sim_data["DATE"].dropna()).unique()
            obs_dates = pd.to_datetime(obs_data["DATE"].dropna())
            date_to_xvar = dict(zip(sim_dates, sim_data[f"{x_var}"].dropna().unique()))
            obs_data[f"{x_var}"] = obs_dates.map(date_to_xvar)
            
            if obs_data[f"{x_var}"].isna().any():
                logger.warning(f"Some values for {x_var} could not be inferred from simulation data")
        else:
            logger.warning("Simulation data does not have 'DATE' column")
            
    # Create sequence as last resort
    if f"{x_var}" not in obs_data.columns:
        logger.warning(f"Creating sequence for missing {x_var} in observed data")
        obs_data[f"{x_var}"] = range(len(obs_data))
        
    obs_data[f"{x_var}"].fillna(method="ffill", inplace=True)
    return obs_data

def parse_data_cde(data_cde_path: str = None) -> dict:
    """Parse DATA.CDE file and return a dictionary of variable information."""
    if data_cde_path is None:
        from config import DSSAT_BASE
        data_cde_path = f"{DSSAT_BASE}/DATA.CDE"
        
    variable_info = {}
    try:
        with open(data_cde_path, "r") as f:
            lines = f.readlines()
            
        # Filter relevant lines
        data_lines = [line for line in lines if not line.startswith(("!", "*"))]
        header_line = next(line for line in data_lines if line.startswith("@"))
        
        # Process data lines
        for line in data_lines[data_lines.index(header_line) + 1:]:
            if len(line.strip()) == 0:
                continue
                
            cde = line[0:6].strip()
            label = line[7:20].strip()
            description = line[21:70].strip() if len(line) > 21 else ""
            
            if cde:
                variable_info[cde] = {"label": label, "description": description}
                
    except Exception as e:
        logger.error(f"Error parsing DATA.CDE: {e}")
        
    return variable_info

def get_variable_info(variable_name: str, data_cde_path: str = None) -> tuple:
    """Get label and description for a variable."""
    try:
        variable_info = parse_data_cde(data_cde_path)
        if variable_name in variable_info:
            return (
                variable_info[variable_name]["label"],
                variable_info[variable_name]["description"],
            )
        return None, None
        
    except Exception as e:
        logger.error(f"Error getting variable info: {e}")
        return None, None

def get_evaluate_variable_pairs(data: pd.DataFrame) -> List[Tuple[str, str, str]]:
    """
    Get pairs of simulated and measured variables from EVALUATE.OUT data.
    Returns list of tuples (base_name, sim_var, meas_var)
    Filters out pairs where:
    1. Either simulated or measured values are all missing
    2. The simulated and measured values are identical
    """
    pairs = []
    columns = set(data.columns)
    
    for col in columns:
        # Skip metadata columns
        if col in ['RUN', 'EXCODE', 'TRNO', 'RN', 'CR']:
            continue
            
        # Check if this is a simulated variable (ends with S)
        if col.endswith('S'):
            base_name = col[:-1]
            measured_var = base_name + 'M'
            
            # Check if we have the matching measured variable
            if measured_var in columns:
                # Skip if either variable has all missing values
                sim_all_missing = data[col].isna().all()
                meas_all_missing = data[measured_var].isna().all()
                
                if sim_all_missing or meas_all_missing:
                    continue
                
                # Get valid pairs (drop NA values from both columns)
                valid_data = data[[col, measured_var]].dropna()
                
                # Skip if no valid data points after dropping NAs
                if valid_data.empty:
                    continue
                    
                # Skip if all simulated values equal all measured values
                if (valid_data[col] == valid_data[measured_var]).all():
                    logger.info(f"Skipping {base_name} - all simulated and measured values are identical")
                    continue
                
                # Get variable info for nice display
                var_label, _ = get_variable_info(base_name)
                display_name = var_label if var_label else base_name
                pairs.append((display_name, col, measured_var))
                
    return sorted(pairs)

def get_all_evaluate_variables(data: pd.DataFrame) -> List[Tuple[str, str]]:
    """Get all variables from EVALUATE.OUT data with their descriptions.
    Filters out variables that have all missing values."""
    variables = []
    for col in data.columns:
        if col not in ['RUN', 'EXCODE', 'TRNO', 'RN', 'CR']:
            # Check if variable has any non-missing values
            if not data[col].isna().all():
                var_label, _ = get_variable_info(col)
                display_name = var_label if var_label else col
                variables.append((display_name, col))
    return sorted(variables)

def improved_smart_scale(
    data, variables, target_min=1000, target_max=10000, scaling_factors=None
):
    """Scale data columns to a target range for visualization."""
    scaled_data = {}
    available_vars = [var for var in variables if var in data.columns]
    for var in available_vars:
        values = pd.to_numeric(data[var], errors="coerce").dropna().values
        if len(values) == 0:
            continue
        if scaling_factors and var in scaling_factors:
            scale_factor, offset = scaling_factors[var]
        else:
            var_min, var_max = np.min(values), np.max(values)
            if np.isclose(var_min, var_max):
                midpoint = (target_max + target_min) / 2
                scaled_data[var] = pd.Series(
                    [midpoint] * len(data[var]), index=data[var].index
                )
                continue
            scale_factor = (target_max - target_min) / (var_max - var_min)
            offset = target_min - var_min * scale_factor
        numeric_data = pd.to_numeric(data[var], errors="coerce")
        scaled_data[var] = numeric_data * scale_factor + offset
    return scaled_data
