import numpy as np
import sys
sys.dont_write_bytecode = True

# sim_thres = 0.1
# sim = np.array([[0.2, 0.02, 0.1], [0.02, 0.02, 0.11], [0.02, 0.2, 0.11]])
# def compare_and_filter(similarities):
#     thres_matrix = np.ones(similarities.shape) * sim_thres
#     mask_matrix = np.greater(similarities, thres_matrix)
#     return np.where(mask_matrix, sim, 0)
# print(compare_and_filter(sim))
arr = np.array([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
print(arr/np.array([np.abs(arr).sum(axis=0)]))
print(arr/np.array([np.abs(arr).sum(axis=1)]).T)