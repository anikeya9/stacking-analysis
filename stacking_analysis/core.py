"""
Core stacking analysis functions.

This module contains the main computational logic for identifying
and classifying stacking configurations in bilayer materials.
"""

import numpy as np
from numba import jit


@jit(nopython=True, nogil=True)
def classify_stacking_type(atom, df_numpy, r_tol=0.614, s_neighbor_distance=3.0):
    """
    Classify the stacking type for a given atom based on its local environment.
    
    This function analyzes the local atomic environment to determine the stacking
    configuration (AA, AA', A'B, AB, AB', BA, or X).
    
    Parameters
    ----------
    atom : numpy.ndarray
        Array representing the atom [id, type, x, y, z, ...]
    df_numpy : numpy.ndarray
        Array of all atoms in the neighborhood
    r_tol : float, optional
        Distance tolerance for neighbor identification (default: 0.614)
    s_neighbor_distance : float, optional
        Distance threshold for S-type neighbors (default: 3.0)
    
    Returns
    -------
    tuple
        (atom_id, stacking_type, stacking_code)
        where stacking_type is a string (e.g., 'AA', 'AB')
        and stacking_code is an integer (0-6)
    
    Notes
    -----
    Stacking types and their codes:
    - BA: 0
    - AB: 1
    - AA': 2
    - A'B: 3
    - AB': 4
    - AA: 5
    - X (unclassified): 6
    """
    
    # Custom function to replace np.isin for numba compatibility
    def isin(a, b):
        """Check if all elements in a are in b."""
        for i in a:
            if i not in b:
                return False
        return True
    
    idx = int(atom[0])
    vector = []
    
    # Calculate distances to all atoms in xy-plane
    distances = np.sqrt((df_numpy[:, 2] - atom[2]) ** 2 +  
                        (df_numpy[:, 3] - atom[3]) ** 2)  

    # Find central Mo atoms (type != 4)
    cent_mo = df_numpy[(distances <= r_tol) & (df_numpy[:, 1] != 4)] 

    # Classify central Mo configuration
    if len(cent_mo) == 0:
        vector.append(0)
    elif len(cent_mo) == 1:
        if cent_mo[0][1] == 1:
            vector.append(1)
        else:
            vector.append(20)
    elif len(cent_mo) == 2:
        if isin(cent_mo[:, 1], [2, 3]):
            vector.append(2)
        else:
            vector.append(20)
    else:
        vector.append(20)

    # Find top S neighbors (type == 6)
    top_s_neighbors = df_numpy[(distances <= s_neighbor_distance) & (df_numpy[:, 1] == 6)]  
    
    # Analyze each S neighbor
    if len(top_s_neighbors) == 3:
        for s_atom in top_s_neighbors:
            s_distances = np.sqrt((df_numpy[:, 2] - s_atom[2])**2 +  
                                  (df_numpy[:, 3] - s_atom[3])**2)
            cent_s = df_numpy[(s_distances <= r_tol) & (df_numpy[:, 1] != 6)]
            
            if len(cent_s) == 0:
                vector.append(20)
            elif len(cent_s) == 1:
                if cent_s[0][1] == 5:
                    vector.append(1)
                else:
                    vector.append(20)
            elif len(cent_s) == 2:
                if isin(cent_s[:, 1], [1, 5]):
                    vector.append(2)
                else:
                    vector.append(20)
            elif len(cent_s) == 3:
                if isin(cent_s[:, 1], [2, 3, 5]):
                    vector.append(3)
                else:
                    vector.append(20)
            else:
                vector.append(20)
    else:
        vector.append(20)

    # Determine stacking type from vector signature
    if vector == [1, 3, 3, 3]:
        s_type = "AA"
    elif vector == [2, 2, 2, 2]:
        s_type = "AA'"
    elif vector == [1, 1, 1, 1]:
        s_type = "A'B"
    elif vector == [0, 3, 3, 3]:
        s_type = "AB'"
    elif vector == [0, 2, 2, 2]:
        s_type = "AB"
    elif vector == [2, 1, 1, 1]:
        s_type = "BA"
    else:
        s_type = "X"
    
    # Map stacking type to numeric code
    stacking_codes = {
        "A'B": 3,
        "BA": 0,
        "AB": 1,
        "AA'": 2,
        "AB'": 4,
        "AA": 5,
        "X": 6
    }
    
    s_code = stacking_codes[s_type]
    
    return idx, s_type, s_code
