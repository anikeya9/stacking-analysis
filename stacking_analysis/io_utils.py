"""
Input/Output utilities for stacking analysis.

This module handles reading input files and writing output files
in various formats.
"""

import pandas as pd


def read_structure_file(filepath, skiprows=9, 
                       columns=None):
    """
    Read atomic structure file.
    
    Parameters
    ----------
    filepath : str
        Path to the input structure file
    skiprows : int, optional
        Number of header rows to skip (default: 9)
    columns : list, optional
        Column names. If None, uses default columns:
        ['id', 'type', 'x', 'y', 'z', 'fx', 'fy', 'fz', 'c_myPE']
    
    Returns
    -------
    pandas.DataFrame
        DataFrame containing atomic structure data
    
    Raises
    ------
    FileNotFoundError
        If the input file does not exist
    ValueError
        If the file format is invalid
    """
    if columns is None:
        columns = ["id", "type", "x", "y", "z", "fx", "fy", "fz", "c_myPE"]
    
    try:
        df = pd.read_csv(filepath, sep=" ", skiprows=skiprows, names=columns)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading file {filepath}: {str(e)}")
    
    # Validate required columns
    required_cols = ['id', 'type', 'x', 'y', 'z']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return df


def write_xyz(filepath, atom_data):
    """
    Write atomic data to XYZ-style output file.
    
    Parameters
    ----------
    filepath : str
        Path to output file
    atom_data : pandas.DataFrame
        DataFrame containing atomic data to write
    
    Notes
    -----
    The output format includes:
    - First line: number of atoms
    - Remaining lines: atom data in space-separated format
    """
    with open(filepath, 'w') as file:
        # Write number of atoms
        file.write(f"{len(atom_data)}\n")
        # Write atom data
        atom_data.to_csv(file, sep=' ', index=False, header=True, mode='a')


def write_results_csv(filepath, results_df):
    """
    Write analysis results to CSV file.
    
    Parameters
    ----------
    filepath : str
        Path to output CSV file
    results_df : pandas.DataFrame
        DataFrame containing analysis results
    """
    results_df.to_csv(filepath, index=False)
