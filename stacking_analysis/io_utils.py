"""
Input/Output utilities for stacking analysis.

This module handles reading LAMMPS dump files and writing output files
in various formats.
"""

import pandas as pd
import re


def parse_lammps_dump_columns(filepath):
    """
    Parse column names from LAMMPS dump file header (line 9).
    
    Parameters
    ----------
    filepath : str
        Path to LAMMPS dump file
    
    Returns
    -------
    list
        List of column names extracted from the ITEM: ATOMS line
    
    Examples
    --------
    For a line like "ITEM: ATOMS id type x y z fx fy fz"
    Returns: ['id', 'type', 'x', 'y', 'z', 'fx', 'fy', 'fz']
    """
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            if i == 8:  # Line 9 (0-indexed as line 8)
                # Extract everything after "ITEM: ATOMS"
                if 'ITEM: ATOMS' in line or 'ITEM:ATOMS' in line:
                    # Split and get everything after ATOMS
                    parts = re.split(r'ITEM:\s*ATOMS\s+', line)
                    if len(parts) > 1:
                        columns = parts[1].strip().split()
                        return columns
                    else:
                        # Fallback: split by whitespace and skip first parts
                        parts = line.strip().split()
                        # Find index of 'ATOMS' and return everything after
                        if 'ATOMS' in parts:
                            idx = parts.index('ATOMS')
                            return parts[idx+1:]
                break
    
    # If we couldn't parse, return None
    return None


def read_structure_file(filepath, skiprows=9, columns=None):
    """
    Read LAMMPS dump file (single frame).
    
    This function automatically reads column names from the LAMMPS dump file
    header (line 9: "ITEM: ATOMS ..."). It requires the first 5 columns to be
    id, type, x, y, z (in that order). Additional columns are read but not
    required for analysis.
    
    Parameters
    ----------
    filepath : str
        Path to the input LAMMPS dump file (single frame)
    skiprows : int, optional
        Number of header rows to skip (default: 9 for LAMMPS dump format)
    columns : list, optional
        Column names. If None, automatically parses from line 9 of dump file.
        If parsing fails, uses default columns.
    
    Returns
    -------
    pandas.DataFrame
        DataFrame containing atomic structure data
    
    Raises
    ------
    FileNotFoundError
        If the input file does not exist
    ValueError
        If the file format is invalid or required columns are missing
    
    Notes
    -----
    LAMMPS dump file format (single frame):
    Line 1: ITEM: TIMESTEP
    Line 2: <timestep>
    Line 3: ITEM: NUMBER OF ATOMS
    Line 4: <number>
    Line 5: ITEM: BOX BOUNDS ...
    Line 6-8: <box bounds>
    Line 9: ITEM: ATOMS id type x y z [additional columns...]
    Line 10+: <atom data>
    
    Required columns (first 5): id, type, x, y, z
    Additional columns are optional and will be preserved.
    
    Examples
    --------
    # Standard usage (auto-detect columns)
    >>> df = read_structure_file('dump.lammpstrj')
    
    # With custom columns (if auto-detection fails)
    >>> df = read_structure_file('dump.lammpstrj', 
    ...                          columns=['id', 'type', 'x', 'y', 'z', 'fx', 'fy', 'fz'])
    """
    
    # Try to auto-detect columns from file
    if columns is None:
        columns = parse_lammps_dump_columns(filepath)
        
        if columns is None:
            # Fallback to default columns
            print("Warning: Could not auto-detect columns from LAMMPS dump file.")
            print("Using default columns: ['id', 'type', 'x', 'y', 'z', 'fx', 'fy', 'fz', 'c_myPE']")
            columns = ["id", "type", "x", "y", "z", "fx", "fy", "fz", "c_myPE"]
        else:
            print(f"Auto-detected columns: {columns}")
    
    try:
        df = pd.read_csv(filepath, sep=r'\s+', skiprows=skiprows, names=columns, 
                        engine='python')
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading file {filepath}: {str(e)}")
    
    # Validate required columns (first 5 must be id, type, x, y, z)
    required_cols = ['id', 'type', 'x', 'y', 'z']
    
    if len(df.columns) < 5:
        raise ValueError(f"File must have at least 5 columns (id, type, x, y, z). Found: {df.columns.tolist()}")
    
    # Check that first 5 columns are the required ones
    first_five = df.columns[:5].tolist()
    for i, (expected, actual) in enumerate(zip(required_cols, first_five)):
        if expected != actual:
            raise ValueError(
                f"Column {i+1} must be '{expected}', but found '{actual}'. "
                f"Required column order: id, type, x, y, z [optional columns...]"
            )
    
    # Issue warning if we have fewer than expected columns but requirements are met
    if len(df.columns) < len(columns):
        print(f"Warning: Expected {len(columns)} columns but found {len(df.columns)}. "
              "This may indicate a parsing issue.")
    
    return df


def read_lammps_dump_metadata(filepath):
    """
    Read metadata from LAMMPS dump file header.
    
    Parameters
    ----------
    filepath : str
        Path to LAMMPS dump file
    
    Returns
    -------
    dict
        Dictionary containing metadata:
        - timestep: int
        - n_atoms: int
        - box_bounds: list of tuples [(xlo, xhi), (ylo, yhi), (zlo, zhi)]
        - columns: list of column names
    """
    metadata = {}
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Parse timestep (line 2)
    if len(lines) > 1:
        metadata['timestep'] = int(lines[1].strip())
    
    # Parse number of atoms (line 4)
    if len(lines) > 3:
        metadata['n_atoms'] = int(lines[3].strip())
    
    # Parse box bounds (lines 6-8)
    if len(lines) > 7:
        bounds = []
        for i in range(5, 8):
            parts = lines[i].strip().split()
            bounds.append((float(parts[0]), float(parts[1])))
        metadata['box_bounds'] = bounds
    
    # Parse column names (line 9)
    metadata['columns'] = parse_lammps_dump_columns(filepath)
    
    return metadata


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


def validate_lammps_dump(filepath):
    """
    Validate that a file is a proper single-frame LAMMPS dump file.
    
    Parameters
    ----------
    filepath : str
        Path to file to validate
    
    Returns
    -------
    tuple
        (is_valid: bool, message: str)
    """
    try:
        with open(filepath, 'r') as f:
            lines = [f.readline() for _ in range(10)]
        
        # Check for LAMMPS dump format markers
        if 'ITEM: TIMESTEP' not in lines[0]:
            return False, "Line 1 should contain 'ITEM: TIMESTEP'"
        
        if 'ITEM: NUMBER OF ATOMS' not in lines[2]:
            return False, "Line 3 should contain 'ITEM: NUMBER OF ATOMS'"
        
        if 'ITEM: BOX BOUNDS' not in lines[4]:
            return False, "Line 5 should contain 'ITEM: BOX BOUNDS'"
        
        if 'ITEM: ATOMS' not in lines[8]:
            return False, "Line 9 should contain 'ITEM: ATOMS'"
        
        # Try to parse columns
        columns = parse_lammps_dump_columns(filepath)
        if columns is None:
            return False, "Could not parse column names from line 9"
        
        if len(columns) < 5:
            return False, f"Need at least 5 columns (id, type, x, y, z), found {len(columns)}"
        
        required = ['id', 'type', 'x', 'y', 'z']
        for i, req in enumerate(required):
            if i >= len(columns) or columns[i] != req:
                return False, f"Column {i+1} should be '{req}', found '{columns[i] if i < len(columns) else 'missing'}'"
        
        return True, "Valid LAMMPS dump file"
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"
