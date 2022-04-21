# encoding:utf-8
import numpy as np
import itertools
import sys

sys.dont_write_bytecode = True

arr2D = np.array([1, 2, 3])

# Find index of maximum value from 2D numpy array
result = np.where(arr2D == np.amax(arr2D))
print('Tuple of arrays returned : ', result)
print('List of coordinates of maximum value in Numpy array : ')
# zip the 2 arrays to get the exact coordinates
listOfCordinates = list(zip(result[0], result[1]))
print(listOfCordinates)
# travese over the list of cordinates
for cord in listOfCordinates:
    print(cord)