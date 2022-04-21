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
from algos import AlgosOperator, ItemCF, UserCF, HybridCF
import utils


if __name__ == "__main__":
    utils.create_folder_paths()
    # visualization.cleaned_data_vis("data_20220222.xlsx")

    mydb = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))

    algos = AlgosOperator(mydb)
    # params, itemCF_fscores = algos.itemCF_tuning(np.arange(0.5, 0.8, 0.03), np.arange(0, 0.2, 0.04))
    # params, userCF_fscores = algos.userCF_tuning(np.arange(0.2, 0.4, 0.02), np.arange(0.12, 0.24, 0.02))

    # visualization.itemCF_tuning_vis()
    # visualization.userCF_tuning_vis()

    # iteration = 20
    # arr = np.zeros(iteration, dtype=float)
    # for i in range(iteration):
    #     arr[i] = algos.calc_train_test_ratio()
    # print(np.average(arr))

    algos.store_metrics_of_all_algos(2)
