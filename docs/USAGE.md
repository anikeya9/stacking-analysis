# Stacking Analysis - Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Command-Line Interface](#command-line-interface)
3. [Python API](#python-api)
4. [Understanding Parameters](#understanding-parameters)
5. [Output Interpretation](#output-interpretation)
6. [Advanced Topics](#advanced-topics)

---

## Getting Started

### Installation Check

After installation, verify everything works:

```bash
python stacking_cli.py --version
```

### Prepare Your Data

Your input file should be a space-separated text file with atomic coordinates. Example format:

```
# Header line 1
# Header line 2
...
# Header line 9
1  1    0.000   0.000   0.000   0.0  0.0  0.0  -3.2
2  4    1.584   0.915   3.172   0.0  0.0  0.0  -3.1
3  6    0.000   1.830   1.586   0.0  0.0  0.0  -2.8
```

Columns: `id`, `type`, `x`, `y`, `z`, `fx`, `fy`, `fz`, `c_myPE`

---

## Command-Line Interface

### Basic Commands

```bash
# Simplest usage
python stacking_cli.py input.xyz

# Specify output location
python stacking_cli.py input.xyz -o /path/to/output.stack

# Custom parameters
python stacking_cli.py input.xyz --r-tol 0.7 --voxel-size 200
```

### All CLI Options

```bash
python stacking_cli.py --help
```

**Positional Arguments:**
- `input`: Path to input structure file

**Optional Arguments:**
- `-o, --output`: Output file path (default: `INPUT.stack`)
- `--r-tol`: Distance tolerance in Å (default: 0.614)
- `--voxel-size`: Spatial partition size in Å (default: 150.0)
- `--s-distance`: S-neighbor distance threshold in Å (default: 3.0)
- `--processes`: Number of CPU cores to use (default: all)
- `--skiprows`: Header lines to skip (default: 9)
- `--atom-type`: Atom type to analyze (default: 4)
- `-q, --quiet`: Suppress progress output
- `--version`: Show version information

### Examples

**Use 4 CPU cores:**
```bash
python stacking_cli.py input.xyz --processes 4
```

**Different distance tolerance:**
```bash
python stacking_cli.py input.xyz --r-tol 0.7
```

**Larger voxel size for huge systems:**
```bash
python stacking_cli.py input.xyz --voxel-size 300
```

**Quiet mode (no progress bars):**
```bash
python stacking_cli.py input.xyz --quiet
```

---

## Python API

### Basic Usage

```python
from stacking_analysis import StackingAnalyzer

# Create analyzer with default settings
analyzer = StackingAnalyzer()

# Load structure
analyzer.load_structure('input.xyz')

# Run analysis
analyzer.analyze()

# Save results
analyzer.save_results('output.stack')
```

### Method Chaining

```python
from stacking_analysis import StackingAnalyzer

# All in one line
analyzer = (StackingAnalyzer()
            .load_structure('input.xyz')
            .analyze()
            .save_results('output.stack'))
```

### Custom Configuration

```python
from stacking_analysis import StackingAnalyzer

analyzer = StackingAnalyzer(
    r_tol=0.7,                    # Custom distance tolerance
    voxel_size=200.0,             # Larger voxels
    s_neighbor_distance=3.5,      # Different threshold
    n_processes=8,                # Use 8 cores
    verbose=True                  # Show progress
)

analyzer.load_structure('input.xyz', skiprows=9)
analyzer.analyze()
analyzer.save_results('output.stack', atom_type=4)
```

### Getting Statistics

```python
# After analysis
stats = analyzer.get_statistics()

print(f"Total atoms: {stats['total_atoms']}")
print("\nCounts by type:")
for s_type, count in stats['type_counts'].items():
    percentage = stats['type_percentages'][s_type]
    print(f"  {s_type}: {count} ({percentage:.1f}%)")
```

### Accessing Raw Data

```python
# Get results DataFrame
results = analyzer.results_df
print(results.head())

# Get full DataFrame with coordinates
full_data = analyzer.df

# Filter specific stacking types
aa_stacking = results[results['S_TYPE'] == 'AA']
ab_stacking = results[results['S_TYPE'] == 'AB']

# Export to CSV
results.to_csv('detailed_results.csv', index=False)
```

---

## Understanding Parameters

### r_tol (Distance Tolerance)

**Default**: 0.614 Å  
**Purpose**: Maximum distance to identify atoms in the same vertical stack

**When to adjust:**
- Material has different lattice parameters
- Thermal expansion/contraction in your data
- Different layer separation

**Example:**
```python
# Larger tolerance for thermally expanded structures
analyzer = StackingAnalyzer(r_tol=0.7)
```

### voxel_size (Spatial Partition Size)

**Default**: 150.0 Å  
**Purpose**: Size of spatial regions for parallel processing

**When to adjust:**
- **Increase** (200-300 Å): For very large systems (>10M atoms)
- **Decrease** (100 Å): For small systems or many cores

**Trade-offs:**
- Larger: Less overhead, more memory per core
- Smaller: Better load balancing, less memory

### s_neighbor_distance

**Default**: 3.0 Å  
**Purpose**: Maximum distance to find sulfur neighbors

**Material-specific:** Adjust based on your material's bond lengths

---

## Output Interpretation

### Output File Structure

```
12345
id type x y z ... S_TYPE S_CODE
1  4    0.0 0.0 0.0 ... AA     5
2  4    1.5 1.5 0.0 ... AB     1
...
```

### Stacking Types Explained

| Type | Code | Physical Meaning |
|------|------|-----------------|
| **AA** | 5 | Perfect vertical alignment |
| **AA'** | 2 | AA with rotation |
| **A'B** | 3 | A'B configuration |
| **AB** | 1 | Most common AB stacking |
| **AB'** | 4 | AB with modification |
| **BA** | 0 | Inverted AB |
| **X** | 6 | Unclassified/defect |

### Typical Distributions

For pristine MoS₂ bilayers:
- AB stacking: ~60-80%
- AA stacking: ~10-20%
- Others: ~10-20%

**High X percentage (>30%)** may indicate:
- Incorrect parameters (r_tol, s_distance)
- Defective structure
- Non-TMD material

---

## Advanced Topics

### Batch Processing

```python
import glob
from stacking_analysis import StackingAnalyzer

# Process all .xyz files in a directory
for input_file in glob.glob('data/*.xyz'):
    output_file = input_file.replace('.xyz', '.stack')
    
    (StackingAnalyzer(verbose=False)
     .load_structure(input_file)
     .analyze()
     .save_results(output_file))
    
    print(f"Processed: {input_file}")
```

### Custom Analysis

```python
from stacking_analysis import StackingAnalyzer
import matplotlib.pyplot as plt

# Run analysis
analyzer = StackingAnalyzer()
analyzer.load_structure('input.xyz')
analyzer.analyze()

# Get results
results = analyzer.df

# Create spatial distribution plot
fig, ax = plt.subplots(figsize=(10, 8))

for s_type, color in [('AA', 'red'), ('AB', 'blue'), ('X', 'gray')]:
    data = results[results['S_TYPE'] == s_type]
    ax.scatter(data['x'], data['y'], c=color, label=s_type, alpha=0.5)

ax.legend()
ax.set_xlabel('x (Å)')
ax.set_ylabel('y (Å)')
ax.set_title('Stacking Type Spatial Distribution')
plt.savefig('stacking_map.png', dpi=300)
```

### Integration with Other Tools

```python
# Export to VMD-compatible format
def export_to_vmd(analyzer, filename):
    """Export colored by stacking type for VMD."""
    df = analyzer.df
    
    # Map stacking types to colors
    color_map = {'AA': 1, 'AB': 2, 'AA\'': 3, 'A\'B': 4, 
                 'AB\'': 5, 'BA': 6, 'X': 7}
    
    df['color'] = df['S_TYPE'].map(color_map)
    
    # Write XYZ with color column
    with open(filename, 'w') as f:
        f.write(f"{len(df)}\n")
        f.write("Stacking analysis results\n")
        for _, row in df.iterrows():
            f.write(f"{row['type']} {row['x']:.4f} {row['y']:.4f} "
                   f"{row['z']:.4f} {row['color']}\n")

# Usage
analyzer = StackingAnalyzer()
analyzer.load_structure('input.xyz').analyze()
export_to_vmd(analyzer, 'colored.xyz')
```

### Performance Optimization

For very large systems (>50M atoms):

```python
# Use more aggressive voxel sizing
analyzer = StackingAnalyzer(
    voxel_size=300.0,      # Larger voxels
    n_processes=32,        # Use all cores
    verbose=True
)

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024**3:.2f} GB")
```

---

## Troubleshooting

### Issue: Memory Error

**Cause**: System too large for available RAM

**Solutions:**
```python
# Increase voxel size
analyzer = StackingAnalyzer(voxel_size=300.0)

# Reduce number of processes
analyzer = StackingAnalyzer(n_processes=4)
```

### Issue: All Atoms Classified as 'X'

**Cause**: Parameters don't match your material

**Solutions:**
```bash
# Try different r_tol values
python stacking_cli.py input.xyz --r-tol 0.5
python stacking_cli.py input.xyz --r-tol 0.7
python stacking_cli.py input.xyz --r-tol 0.8
```

### Issue: Very Slow Performance

**Causes & Solutions:**

1. **Too many small voxels**: Increase voxel_size
2. **Single-threaded**: Check --processes setting
3. **I/O bottleneck**: Use SSD storage

---

For more help, see the GitHub issues page or contact the maintainers.
