import requests
import numpy as np
from math import inf
from math import isinf
from python_tsp.heuristics import solve_tsp_local_search
from python_tsp.exact import solve_tsp_dynamic_programming


DEPOT = {
    'longtitude': 106.625786,
    'latitude': 10.810676
}
TREATMENT_PLANT = {
    'longtitude': 106.628212,
    'latitude': 10.811756
}
THRESHOLD = 0.15
def MakeDistanceMatrix(data):
    data.insert(0, TREATMENT_PLANT)  # dest
    data.insert(0, DEPOT)  # src

    final_URL = 'http://127.0.0.1:5000/table/v1/driving/'
    for item in data:
        final_URL += str(item['longtitude']) + ',' + str(item['latitude']) + ';'
    final_URL = final_URL.rstrip(';')
    final_URL += '?annotations=distance'
    response = requests.get(final_URL).json() # query api for part of the matrix

    right_corner = np.array(response['distances'])
    # introduce first node as a dummy and extending the distance matrix
    row = np.array([np.append(np.array([0, 0]), np.asarray([inf for _ in range(len(data) - 2)]))])
    col = np.array([np.append(np.array([0]), row)]).T
    dist_matrix = np.c_[col, np.r_[row, right_corner]]
    return dist_matrix
def FindOrder(data):
    # return a permutation array and the total distance
    dist_matrix = MakeDistanceMatrix(data)
    if len(data) <= 10: # exact search when the number of MCPs is small
        permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
    else:
        # local search when the number of MCPs is big
        permutation, distance = solve_tsp_local_search(dist_matrix)
        while isinf(distance): # redo until distance is finite
            permutation, distance = solve_tsp_local_search(dist_matrix)
    # trim the dummy node and return ascending orders of MCPs
    if permutation[1] == 1:
        return np.array(permutation[2:-1])-3, distance
    return np.array(permutation[-2:1:-1])-3, distance