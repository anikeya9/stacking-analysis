# Stacking Analysis

> A high-performance tool for analyzing atomic stacking configurations in bilayer materials

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## Overview

**Stacking Analysis** is a computational tool designed for identifying and classifying atomic stacking configurations in bilayer transition metal dichalcogenides (TMDs) and similar layered materials. It uses spatial partitioning and parallel processing to efficiently analyze large-scale atomic structures.

### Key Features

- 🚀 **High Performance**: Parallel processing with automatic CPU core detection
- 🎯 **Accurate Classification**: Identifies 6 distinct stacking types (AA, AA', A'B, AB, AB', BA)
- 📊 **Comprehensive Output**: Detailed statistics and labeled atomic structures
- 🔧 **Flexible Configuration**: Customizable parameters for different material systems
- 💻 **Easy to Use**: Simple command-line interface and Python API

## Citation

If you use this software in your research, please cite our paper:

```bibtex
@article{doi:10.1021/acsnano.5c14092,
author = {Aditya, Anikeya and Irie, Ayu and Dasgupta, Nabankur and Kalia, Rajiv K. and Nakano, Aiichiro and Vashishta, Priya},
title = {Emerging Ferroelectric Domains: Stacking and Rotational Landscape of MoS2 Moiré Bilayers},
journal = {ACS Nano},
volume = {0},
number = {0},
pages = {null},
year = {0},
doi = {10.1021/acsnano.5c14092},
    note ={PMID: 41648955},

URL = { 
    
        https://doi.org/10.1021/acsnano.5c14092
    
    

},
eprint = { 
    
        https://doi.org/10.1021/acsnano.5c14092
    
    

}

}
```

**Paper**: [\[Link to published paper\]  ](https://doi.org/10.1021/acsnano.5c14092)
**DOI**: `10.1021/acsnano.5c14092`

## Installation

### Requirements

- Python 3.7 or higher
- NumPy >= 1.20.0
- Pandas >= 1.3.0
- Numba >= 0.54.0
- Matplotlib >= 3.4.0 (optional, for visualization)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/anikeya9/stacking-analysis.git
cd stacking-analysis

# Install dependencies
pip install -r requirements.txt
```

### Quick Install (Future)

```bash
pip install stacking-analysis
```

## Quick Start

### Command-Line Usage

```bash
# Basic usage
python stacking_cli.py input.xyz

# Specify output file
python stacking_cli.py input.xyz -o results.stack

# Custom parameters
python stacking_cli.py input.xyz --r-tol 0.7 --voxel-size 200

# Use specific number of CPU cores
python stacking_cli.py input.xyz --processes 8

# Quiet mode (no progress output)
python stacking_cli.py input.xyz --quiet
```

### Python API Usage

```python
from stacking_analysis import StackingAnalyzer

# Create analyzer
analyzer = StackingAnalyzer()

# Load, analyze, and save (method chaining)
analyzer.load_structure('input.xyz').analyze().save_results('output.stack')

# Get statistics
stats = analyzer.get_statistics()
print(stats)
```

## Input Format

The input file should be a space-separated text file with the following columns:

```
id type x y z fx fy fz c_myPE
1  1    0.0 0.0 0.0 0.0 0.0 0.0 -3.2
2  4    1.5 1.5 3.2 0.0 0.0 0.0 -3.1
...
```

**Required columns**: `id`, `type`, `x`, `y`, `z`

The file should have a 9-line header (customizable with `--skiprows`).

## Output Format

The output `.stack` file contains all atoms of the specified type (default: type 4) with additional columns:

- `S_TYPE`: Stacking type classification (AA, AA', A'B, AB, AB', BA, or X)
- `S_CODE`: Numeric code for the stacking type (0-6)

### Stacking Type Codes

| Type | Code | Description |
|------|------|-------------|
| BA   | 0    | BA stacking |
| AB   | 1    | AB stacking |
| AA'  | 2    | AA' stacking |
| A'B  | 3    | A'B stacking |
| AB'  | 4    | AB' stacking |
| AA   | 5    | Perfect AA stacking |
| X    | 6    | Unclassified |

## Advanced Usage

### Custom Parameters

```python
from stacking_analysis import StackingAnalyzer

analyzer = StackingAnalyzer(
    r_tol=0.614,              # Distance tolerance (Å)
    voxel_size=150.0,         # Spatial partition size (Å)
    s_neighbor_distance=3.0,  # S-neighbor distance threshold (Å)
    n_processes=8,            # Number of CPU cores
    verbose=True              # Print progress
)

analyzer.load_structure('input.xyz', skiprows=9)
analyzer.analyze()
analyzer.save_results('output.stack', atom_type=4)
```

### Accessing Results Programmatically

```python
# Get the results DataFrame
results_df = analyzer.results_df

# Filter by stacking type
aa_atoms = results_df[results_df['S_TYPE'] == 'AA']

# Get full dataset with coordinates
full_data = analyzer.df

# Export to CSV
results_df.to_csv('results.csv', index=False)
```

## Examples

See the [`examples/`](examples/) directory for more usage examples:

- `usage_example.py`: Comprehensive Python API examples
- Additional example data files (coming soon)

## Performance

Typical performance on a modern workstation:

## Algorithm Details

The classification algorithm:

1. **Spatial Partitioning**: Divides the structure into overlapping voxels
2. **Local Environment Analysis**: For each target atom, identifies neighbors within distance thresholds
3. **Pattern Recognition**: Classifies stacking based on local coordination patterns
4. **Parallel Processing**: Processes voxels independently across multiple CPU cores

### Parameters

- **r_tol** (0.614 Å): Distance tolerance for identifying nearest neighbors in the stacking direction
- **voxel_size** (150 Å): Size of spatial partitions; larger values reduce overhead but increase memory usage
- **s_neighbor_distance** (3.0 Å): Maximum distance for identifying sulfur neighbors

These defaults are optimized for MoS₂ bilayers but can be adjusted for other materials.

## Troubleshooting

### Common Issues

**Problem**: "FileNotFoundError"
```bash
# Solution: Check your input file path
ls input.xyz  # Verify file exists
```

**Problem**: Slow performance
```bash
# Solution: Adjust voxel size or number of processes
python stacking_cli.py input.xyz --voxel-size 200 --processes 16
```

**Problem**: All atoms classified as 'X'
```bash
# Solution: Adjust distance tolerance
python stacking_cli.py input.xyz --r-tol 0.7
```

## Contributing

Contributions are welcome! Please feel free to:

- Report bugs by opening an issue
- Suggest features or improvements
- Submit pull requests

## Development

### Running Tests (Future)

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Anikeya Aditya** - [GitHub](https://github.com/anikeya9)

## Acknowledgments

- This research was supported by the U.S. Department of Energy, Office of Basic Energy Sciences, Division of Materials Sciences and Engineering, Neutron Scattering and Instrumentation Sciences program under award DE-SC0023146.
- Computational resources from USC CARC
- Based on research published in ACS Nano

## Contact

For questions or support:
- **GitHub Issues**: https://github.com/anikeya9/stacking-analysis/issues

---
