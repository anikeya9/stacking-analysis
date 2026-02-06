#!/usr/bin/env python3
"""
Example usage of the stacking analysis package.

This script demonstrates how to use the StackingAnalyzer class
programmatically in your own Python code.
"""

from stacking_analysis import StackingAnalyzer


def example_basic_usage():
    """Basic usage example."""
    print("="*60)
    print("BASIC USAGE EXAMPLE")
    print("="*60)
    
    # Create analyzer with default parameters
    analyzer = StackingAnalyzer()
    
    # Load structure, analyze, and save results
    analyzer.load_structure('input.xyz')
    analyzer.analyze()
    analyzer.save_results('output.stack')


def example_custom_parameters():
    """Example with custom parameters."""
    print("\n" + "="*60)
    print("CUSTOM PARAMETERS EXAMPLE")
    print("="*60)
    
    # Create analyzer with custom parameters
    analyzer = StackingAnalyzer(
        r_tol=0.7,              # Custom distance tolerance
        voxel_size=200.0,       # Larger voxels
        s_neighbor_distance=3.5, # Different S-neighbor distance
        n_processes=4,          # Use 4 CPU cores
        verbose=True            # Print progress
    )
    
    # Load and analyze
    analyzer.load_structure('input.xyz', skiprows=9)
    analyzer.analyze()
    analyzer.save_results('custom_output.stack')


def example_with_statistics():
    """Example showing how to get statistics."""
    print("\n" + "="*60)
    print("STATISTICS EXAMPLE")
    print("="*60)
    
    # Create and run analyzer
    analyzer = StackingAnalyzer(verbose=False)
    analyzer.load_structure('input.xyz')
    analyzer.analyze()
    
    # Get statistics
    stats = analyzer.get_statistics()
    
    print(f"Total atoms analyzed: {stats['total_atoms']}")
    print("\nStacking type distribution:")
    for s_type, count in sorted(stats['type_counts'].items()):
        percentage = stats['type_percentages'][s_type]
        print(f"  {s_type}: {count} atoms ({percentage:.2f}%)")


def example_method_chaining():
    """Example using method chaining."""
    print("\n" + "="*60)
    print("METHOD CHAINING EXAMPLE")
    print("="*60)
    
    # All operations in one chain
    stats = (StackingAnalyzer(verbose=True)
             .load_structure('input.xyz')
             .analyze()
             .save_results('output.stack')
             .get_statistics())
    
    print(f"\nProcessed {stats['total_atoms']} atoms")


def example_accessing_results():
    """Example showing how to access raw results."""
    print("\n" + "="*60)
    print("ACCESSING RESULTS EXAMPLE")
    print("="*60)
    
    analyzer = StackingAnalyzer(verbose=False)
    analyzer.load_structure('input.xyz')
    analyzer.analyze()
    
    # Access the results DataFrame
    results = analyzer.results_df
    print(f"Results shape: {results.shape}")
    print("\nFirst few results:")
    print(results.head())
    
    # Access the full DataFrame with original data
    full_df = analyzer.df
    print(f"\nFull data shape: {full_df.shape}")
    print("\nColumns available:")
    print(full_df.columns.tolist())
    
    # Filter for specific stacking types
    aa_stacking = results[results['S_TYPE'] == 'AA']
    print(f"\nNumber of AA stacking atoms: {len(aa_stacking)}")


if __name__ == '__main__':
    print("STACKING ANALYSIS - USAGE EXAMPLES")
    print("="*60)
    print("\nNote: These examples assume you have an 'input.xyz' file.")
    print("Update the file paths to match your data.\n")
    
    # Uncomment the example you want to run:
    
    # example_basic_usage()
    # example_custom_parameters()
    # example_with_statistics()
    # example_method_chaining()
    # example_accessing_results()
    
    print("\nUncomment the examples in the script to run them!")
