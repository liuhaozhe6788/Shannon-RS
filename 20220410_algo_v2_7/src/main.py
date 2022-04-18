# encoding:utf-8
import os
import pandas as pd
import numpy as np
import sys
sys.dont_write_bytecode = True
from icecream import ic

import configs
import database
import visualization
from algos import AlgosOperator
import utils


if __name__ == "__main__":
    # visualization.cleaned_data_vis("data_20220222.xlsx")

    mydb = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))

    algos = AlgosOperator(mydb)
    iteration = 20
    arr = np.zeros(iteration, dtype=float)
    # algos.store_metrics(50)
    for i in range(iteration):
        arr[i] = algos.calc_traib_test_ratio()
    ic(np.average(arr))
