# Stacking Analysis Software

Analysis tool for atomic stacking configurations in layered materials.

## Citation  
If you use this software, please cite our paper:


## Installation 

### Requirements
- Pyhton 3.7+
- NumPy
- Pandas
- Numba
- Matplotlib

### Install Dependencies

pip install -r requirements.txt

## Usage

### Basic Usage
python Stacking_billion_final.py input_file.xyz

### Input Format
The input file should be a space-separated file with columns:
·	id, type, x, y, z, fx, fy, fz, c_myPE

### Output
Generates a .stack file with stacking type classifications:
·	AA: Type 5
·	AA': Type 2
·	A'B: Type 3
·	AB: Type 1
·	AB': Type 4
·	BA: Type 0
·	X: Type 6 (unclassified)

### Parameters
·	r_tol: 0.614 (distance tolerance for neighbor identification)
·	voxel_size: 150 (spatial partitioning size)

### Authors
Anikeya Aditya 

### Contact  

### License 
[Choose: MIT / GPL-3.0 / Apache-2.0]


### Acknowledgments













