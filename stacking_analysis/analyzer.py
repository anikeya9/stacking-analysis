"""
Main analyzer class for stacking configuration analysis.

This module provides the high-level interface for performing
stacking analysis on bilayer structures.
"""

import numpy as np
import pandas as pd
import multiprocessing
import time
from .core import classify_stacking_type
from .io_utils import read_structure_file, write_xyz


class StackingAnalyzer:
    """
    Main class for analyzing stacking configurations in bilayer materials.
    
    Parameters
    ----------
    r_tol : float, optional
        Distance tolerance for neighbor identification (default: 0.614 Å)
    voxel_size : float, optional
        Size of spatial voxels for partitioning (default: 150.0 Å)
    s_neighbor_distance : float, optional
        Distance threshold for S-type neighbors (default: 3.0 Å)
    n_processes : int, optional
        Number of parallel processes. If None, uses all available CPUs.
    verbose : bool, optional
        Print progress information (default: True)
    
    Attributes
    ----------
    df : pandas.DataFrame
        Input atomic structure data
    results_df : pandas.DataFrame
        Analysis results
    """
    
    def __init__(self, r_tol=0.614, voxel_size=150.0, 
                 s_neighbor_distance=3.0, n_processes=None, verbose=True):
        self.r_tol = r_tol
        self.voxel_size = voxel_size
        self.s_neighbor_distance = s_neighbor_distance
        self.n_processes = n_processes or multiprocessing.cpu_count()
        self.verbose = verbose
        
        self.df = None
        self.results_df = None
    
    def load_structure(self, filepath, skiprows=9, columns=None):
        """
        Load atomic structure from file.
        
        Parameters
        ----------
        filepath : str
            Path to input structure file
        skiprows : int, optional
            Number of header rows to skip (default: 9)
        columns : list, optional
            Column names for the file
        
        Returns
        -------
        self
            Returns self for method chaining
        """
        if self.verbose:
            print(f"Loading structure from {filepath}...")
        
        self.df = read_structure_file(filepath, skiprows, columns)
        
        if self.verbose:
            print(f"Loaded {len(self.df)} atoms")
            print(f"Columns: {self.df.columns.tolist()}")
        
        return self
    
    def _create_voxels(self):
        """Create spatial voxel partitions for parallel processing."""
        self.df['voxel_x'] = self.df['x'] // self.voxel_size
        self.df['voxel_y'] = self.df['y'] // self.voxel_size
        
        voxel_x = self.df['voxel_x'].unique()
        voxel_y = self.df['voxel_y'].unique()
        
        patches = [[x, y] for x in voxel_x for y in voxel_y]
        
        if self.verbose:
            print(f"Created {len(patches)} spatial patches")
        
        return patches
    
    def _process_patch(self, patch):
        """
        Process a single spatial patch.
        
        Parameters
        ----------
        patch : list
            [x_id, y_id] coordinates of the patch
        
        Returns
        -------
        list
            List of (atom_id, stacking_type, stacking_code) tuples
        """
        x_id, y_id = patch
        
        # Extract neighborhood (including adjacent voxels)
        small_df = self.df[
            (self.df['voxel_x'] >= (x_id - 1)) & 
            (self.df['voxel_x'] <= (x_id + 1)) &
            (self.df['voxel_y'] >= (y_id - 1)) & 
            (self.df['voxel_y'] <= (y_id + 1))
        ].copy()
        df_numpy = small_df.to_numpy()
        
        # Extract target atoms (type 4 only)
        target_df = self.df[
            (self.df['voxel_x'] == x_id) & 
            (self.df['voxel_y'] == y_id) & 
            (self.df['type'] == 4)
        ].copy()
        target_numpy = target_df.to_numpy()
        
        # Classify each target atom
        results = [
            classify_stacking_type(atom, df_numpy, self.r_tol, self.s_neighbor_distance) 
            for atom in target_numpy
        ]
        
        if self.verbose:
            print(f"Completed patch ({x_id}, {y_id})")
        
        return results
    
    def analyze(self):
        """
        Perform stacking analysis on loaded structure.
        
        Returns
        -------
        self
            Returns self for method chaining
        
        Raises
        ------
        ValueError
            If no structure has been loaded
        """
        if self.df is None:
            raise ValueError("No structure loaded. Call load_structure() first.")
        
        if self.verbose:
            print("\nStarting stacking analysis...")
            print(f"Using {self.n_processes} CPU cores")
        
        # Create spatial patches
        patches = self._create_voxels()
        
        # Process patches in parallel
        start_time = time.time()
        
        with multiprocessing.Pool(processes=self.n_processes) as pool:
            stack_results = pool.map(self._process_patch, patches)
        
        elapsed_time = time.time() - start_time
        
        if self.verbose:
            print(f"\nAnalysis completed in {elapsed_time:.2f} seconds")
        
        # Convert results to DataFrame
        results = []
        for patch_results in stack_results:
            for atom_id, s_type, s_code in patch_results:
                results.append({
                    'id': np.int64(atom_id),
                    'S_TYPE': s_type,
                    'S_CODE': s_code
                })
        
        self.results_df = pd.DataFrame(results)
        
        if self.verbose:
            print(f"Classified {len(self.results_df)} atoms")
            print("\nStacking type distribution:")
            print(self.results_df['S_TYPE'].value_counts().sort_index())
        
        # Merge results with original data
        self.df = pd.merge(self.df, self.results_df, on='id', how='left')
        
        return self
    
    def save_results(self, output_path, atom_type=4):
        """
        Save analysis results to file.
        
        Parameters
        ----------
        output_path : str
            Path to output file
        atom_type : int, optional
            Filter results to specific atom type (default: 4)
        
        Returns
        -------
        self
            Returns self for method chaining
        """
        if self.df is None or 'S_TYPE' not in self.df.columns:
            raise ValueError("No results to save. Run analyze() first.")
        
        # Filter by atom type
        output_df = self.df[self.df['type'] == atom_type].copy()
        
        # Write to file
        write_xyz(output_path, output_df)
        
        if self.verbose:
            print(f"\nResults saved to {output_path}")
            print(f"Saved {len(output_df)} atoms of type {atom_type}")
        
        return self
    
    def get_statistics(self):
        """
        Get statistics about stacking types.
        
        Returns
        -------
        dict
            Dictionary containing stacking type counts and percentages
        """
        if self.results_df is None:
            raise ValueError("No results available. Run analyze() first.")
        
        counts = self.results_df['S_TYPE'].value_counts()
        total = len(self.results_df)
        
        stats = {
            'total_atoms': total,
            'type_counts': counts.to_dict(),
            'type_percentages': (counts / total * 100).to_dict()
        }
        
        return stats
