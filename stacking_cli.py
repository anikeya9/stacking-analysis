#!/usr/bin/env python3
"""
Command-line interface for stacking analysis.

This script provides a user-friendly command-line interface
for analyzing bilayer stacking configurations from LAMMPS dump files.
"""

import argparse
import sys
from stacking_analysis import StackingAnalyzer
from stacking_analysis.io_utils import validate_lammps_dump, read_lammps_dump_metadata


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Analyze stacking configurations in bilayer materials from LAMMPS dump files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dump.lammpstrj
  %(prog)s dump.lammpstrj -o results.stack
  %(prog)s dump.lammpstrj --r-tol 0.7 --voxel-size 200
  %(prog)s dump.lammpstrj --processes 8 --quiet

Input File Format:
  The input must be a single-frame LAMMPS dump file with at least these columns:
    id, type, x, y, z
  
  Additional columns (fx, fy, fz, energies, stresses, etc.) are automatically 
  detected and preserved but not used in the analysis.
  
  To extract a single frame from a multi-frame dump:
    tail -n $((N_atoms + 9)) dump.lammpstrj > single_frame.dump

Stacking Types:
  AA   - Type 5: Perfect AA stacking
  AA'  - Type 2: AA' stacking
  A'B  - Type 3: A'B stacking
  AB   - Type 1: AB stacking
  AB'  - Type 4: AB' stacking
  BA   - Type 0: BA stacking
  X    - Type 6: Unclassified

For more information, visit: https://github.com/anikeya9/stacking-analysis
        """
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        help='Input LAMMPS dump file (single frame)'
    )
    
    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: INPUT.stack)',
        default=None
    )
    
    parser.add_argument(
        '--r-tol',
        type=float,
        default=0.614,
        help='Distance tolerance for neighbor identification (default: 0.614 Å)'
    )
    
    parser.add_argument(
        '--voxel-size',
        type=float,
        default=150.0,
        help='Spatial voxel size for partitioning (default: 150.0 Å)'
    )
    
    parser.add_argument(
        '--s-distance',
        type=float,
        default=3.0,
        help='Distance threshold for S-type neighbors (default: 3.0 Å)'
    )
    
    parser.add_argument(
        '--processes',
        type=int,
        default=None,
        help='Number of parallel processes (default: all CPUs)'
    )
    
    parser.add_argument(
        '--skiprows',
        type=int,
        default=9,
        help='Number of header rows to skip in input file (default: 9 for LAMMPS dump)'
    )
    
    parser.add_argument(
        '--atom-type',
        type=int,
        default=4,
        help='Atom type to analyze and save (default: 4)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate input file format and exit (does not run analysis)'
    )
    
    parser.add_argument(
        '--show-metadata',
        action='store_true',
        help='Show LAMMPS dump file metadata and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate input file if requested
    if args.validate:
        is_valid, message = validate_lammps_dump(args.input)
        if is_valid:
            print(f"✓ {message}")
            print(f"  File: {args.input}")
            return 0
        else:
            print(f"✗ Invalid LAMMPS dump file: {message}", file=sys.stderr)
            print(f"  File: {args.input}", file=sys.stderr)
            return 1
    
    # Show metadata if requested
    if args.show_metadata:
        try:
            metadata = read_lammps_dump_metadata(args.input)
            print(f"LAMMPS Dump File Metadata")
            print(f"=" * 50)
            print(f"File: {args.input}")
            print(f"Timestep: {metadata.get('timestep', 'N/A')}")
            print(f"Number of atoms: {metadata.get('n_atoms', 'N/A')}")
            if 'box_bounds' in metadata:
                bounds = metadata['box_bounds']
                print(f"Box bounds:")
                print(f"  x: {bounds[0][0]:.3f} to {bounds[0][1]:.3f}")
                print(f"  y: {bounds[1][0]:.3f} to {bounds[1][1]:.3f}")
                print(f"  z: {bounds[2][0]:.3f} to {bounds[2][1]:.3f}")
            if 'columns' in metadata:
                print(f"Columns: {metadata['columns']}")
            return 0
        except Exception as e:
            print(f"Error reading metadata: {e}", file=sys.stderr)
            return 1
    
    # Set output path
    if args.output is None:
        args.output = f"{args.input}.stack"
    
    # Quick validation before starting analysis
    if not args.quiet:
        is_valid, message = validate_lammps_dump(args.input)
        if not is_valid:
            print(f"Warning: {message}", file=sys.stderr)
            print("Attempting to proceed anyway...\n", file=sys.stderr)
    
    # Run analysis
    try:
        analyzer = StackingAnalyzer(
            r_tol=args.r_tol,
            voxel_size=args.voxel_size,
            s_neighbor_distance=args.s_distance,
            n_processes=args.processes,
            verbose=not args.quiet
        )
        
        analyzer.load_structure(args.input, skiprows=args.skiprows)
        analyzer.analyze()
        analyzer.save_results(args.output, atom_type=args.atom_type)
        
        if not args.quiet:
            print("\n" + "="*50)
            print("ANALYSIS COMPLETE")
            print("="*50)
            stats = analyzer.get_statistics()
            print(f"\nTotal atoms analyzed: {stats['total_atoms']}")
            print("\nStacking type distribution:")
            for s_type, count in sorted(stats['type_counts'].items()):
                percentage = stats['type_percentages'][s_type]
                print(f"  {s_type:4s}: {count:6d} ({percentage:5.2f}%)")
            print(f"\nOutput written to: {args.output}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTip: Make sure the input file path is correct.", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTip: Use --validate to check if your file format is correct.", file=sys.stderr)
        print("     Use --show-metadata to see file details.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback
            print("\nFull traceback:", file=sys.stderr)
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
