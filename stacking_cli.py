#!/usr/bin/env python3
"""
Command-line interface for stacking analysis.

This script provides a user-friendly command-line interface
for analyzing bilayer stacking configurations.
"""

import argparse
import sys
from stacking_analysis import StackingAnalyzer


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Analyze stacking configurations in bilayer materials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.xyz
  %(prog)s input.xyz -o results.stack
  %(prog)s input.xyz --r-tol 0.7 --voxel-size 200
  %(prog)s input.xyz --processes 8 --quiet

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
        help='Input structure file path'
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
        help='Number of header rows to skip in input file (default: 9)'
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
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Set output path
    if args.output is None:
        args.output = f"{args.input}.stack"
    
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
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
