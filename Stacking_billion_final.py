import numpy as np
import pandas as pd
import math
import time
import sys
from itertools import combinations
import ast
import matplotlib.pyplot as plt
import multiprocessing
import linecache
from numba import jit

@jit(nopython=True, nogil=True)
def stacking_mo(atom, df_numpy):
    # Custom function to replace np.isin
    def isin(a, b):
        for i in a:
            if i not in b:
                return False
        return True
        
    idx = int(atom[0])
    vector = []
    
    distances = np.sqrt((df_numpy[:, 2] - atom[2]) ** 2 +  
                            (df_numpy[:, 3] - atom[3]) ** 2)  

    cent_mo = df_numpy[(distances <= r_tol) & (df_numpy[:, 1] != 4)] 

    if len(cent_mo) == 0:
        vector.append(0)
    elif len(cent_mo) == 1:
        if cent_mo[0][1] == 1:
            vector.append(1)
        else :
            vector.append(20)
    elif len(cent_mo) == 2:
        if isin(cent_mo[:,1],[2, 3]):
            vector.append(2)
        else:
            vector.append(20)
    else:
        vector.append(20)

    top_s_neighbors = df_numpy[(distances <= 3.0) & (df_numpy[:, 1] == 6)]  
    
    if len(top_s_neighbors) == 3:
        for s_atom in top_s_neighbors:
            s_distances = np.sqrt((df_numpy[:, 2] - s_atom[2])**2 +  
                            (df_numpy[:, 3] - s_atom[3])**2)
            cent_s = df_numpy[(s_distances <= r_tol) & (df_numpy[:, 1] != 6)]
            
            if len(cent_s) == 0:
                vector.append(20)
            elif len(cent_s) == 1:
                if (cent_s[0][1] == 5):
                    vector.append(1)
                else:
                    vector.append(20)
            elif len(cent_s) == 2:
                if isin(cent_s[:,1],[1, 5]):
                    vector.append(2)
                else:
                    vector.append(20)
            elif len(cent_s) == 3:
                if isin(cent_s[:,1],[2, 3, 5]):
                    vector.append(3)
                else:
                    vector.append(20)
            else:
                vector.append(20)
    else:
        vector.append(20)

    # vector = np.array(vector)
    # mag = np.sum(vector)
    
    if vector == [1,3,3,3]:
        s_type = "AA"
    elif vector == [2,2,2,2]:
        s_type = "AA'"
    elif vector == [1,1,1,1]:
        s_type = "A'B"
    elif vector == [0,3,3,3]:
        s_type = "AB'"
    elif vector == [0,2,2,2]:
        s_type = "AB"
    elif vector == [2,1,1,1]:
        s_type = "BA"
    else:
        s_type = "X"
        

    if s_type == "A'B":
        s_code = 3
    elif s_type == "BA":
        s_code = 0
    elif s_type == "AB":
        s_code = 1
    elif s_type == "AA'":
        s_code = 2
    elif s_type == "AB'":
        s_code = 4
    elif s_type == "AA":
        s_code = 5
    elif s_type == "X":
        s_code = 6

    

    return idx,s_type,s_code



def process_patch(patch):
    #st = time.time()

    x_id, y_id = patch
    ###############################
    
    small_df = df[(df['voxel_x'] >= (x_id - 1)) & (df['voxel_x'] <= (x_id + 1)) &
                  (df['voxel_y'] >= (y_id - 1)) & (df['voxel_y'] <= (y_id + 1))].copy()
    df_numpy = small_df.to_numpy()

    
    ###############################
    
    target_df = df[(df['voxel_x'] == x_id) & (df['voxel_y'] == y_id)&( df['type'] == 4)].copy()
    target_numpy = target_df.to_numpy()


    stack_results = [stacking_mo(atom, df_numpy) for atom in target_numpy]
    #ils_results_array = np.array(ils_results)
    # np.save(f"test_results/{x_id}_{y_id}", ils_results_array)
    #en = time.time()
    print(f"Done with ({x_id, y_id}")  
    #print(f"Input length = {len(target_df)} | Output length = {len(stack_results)}")
    # del small_df
    # del target_df
    # del df_numpy
    # del target_numpy
    # gc.collect()
    return stack_results


def write_xyz(filename, atom_data):
    # Buffer for all the lines to write
    lines = [
        f"{len(atom_data)} \n"
    ]
    
    # Write the buffer to the file
    with open(filename, 'w') as file:
        file.writelines(lines)
        # Use to_csv for efficient DataFrame writing
        atom_data.to_csv(file, sep=' ', index=False, header=True, mode='a')

##############################################
############# READ STR FILE ##################
##############################################

#cols = ["id", "type", "x", "y", "z", "c_myPE", "c_stress[1]", "c_stress[2]", "c_stress[3]", "c_stress[4]", "c_stress[5]", "c_stress[6]"]

#cols = ["id", "type", "x", "y", "z", "fx", "fy", "fz", "c_myPE", "v_sxx", "v_syy", "v_szz", "v_sxy", "v_sxz", "v_syz"]

cols = ["id", "type", "x", "y", "z", "fx", "fy", "fz", "c_myPE"]

df = pd.read_csv(sys.argv[1], sep = " ", skiprows=9, names = cols)

r_tol = 0.614

cols = df.columns.tolist()

print(cols)

##############################################
# Make sure the cols printed match this order#
#['id', 'type', 'x', 'y', 'z']################
##############################################

# x_min = df['x'].min()
# y_min = df['y'].min()

# df['x'] = df['x']-x_min
# df['y'] = df['y']-y_min

df['voxel_x'] = df['x']//(150)
df['voxel_y'] = df['y']//(150)

voxel_x = df['voxel_x'].unique()
voxel_y = df['voxel_y'].unique()

l = []
for x in voxel_x:
    for y in voxel_y:
        l.append([x,y])

print(f"Number of patches = {len(l)}")

start = time.time()

patches = l

with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    stack_result = pool.map(process_patch, patches)


end = time.time()

print(f"Time taken : {end-start} secs")

print(f" Number of atoms in type 4: {len(df[(df['type'] == 4) ])}")

result_dict = {result[0]: (result[1], result[2]) for patch_results in stack_result for result in patch_results}

sm = 0
result_dict = {}
for i in stack_result:
    for j in i:
        result_dict[np.int64(j[0])] = {'s_type': j[1], 'code': j[2]}
        sm += 1

sums = 0
for key in result_dict.keys():
    sums = sums + 1

print(f" The lengths in result_dict {sm} and number of keys {sums}")


# Create a new DataFrame from your results
results = []
for i in stack_result:
    for j in i:
        results.append({'id': np.int64(j[0]), 'S_TYPE': j[1], 'S_CODE': j[2]})
results_df = pd.DataFrame(results)

print(f" Length of results_df {len(results_df)}")


# Merge the new DataFrame with the existing one
df = pd.merge(df, results_df, on='id', how='left')


if df.isnull().any().any():
    print("The DataFrame has NaN values.")
else:
    print("The DataFrame does not have any NaN values.")

print("#################################################")


df_4 = df[df['type'] == 4].copy()


if df_4.isnull().any().any():
    print("The DataFrame 4 has NaN values.")
else:
    print("The DataFrame 4 does not have any NaN values.")

print("#################################################")


write_xyz(f"{sys.argv[1]}.stack", df_4)


print("All Done")
