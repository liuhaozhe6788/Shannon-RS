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
    params, userCF_fscores = algos.userCF_tuning(np.arange(0, 1, 0.1), np.arange(0, 1, 0.1))

    # iteration = 20
    # arr = np.zeros(iteration, dtype=float)
    # for i in range(iteration):
    #     arr[i] = algos.calc_train_test_ratio()
    # print(np.average(arr))


    # item_cf = ItemCF(mydb, "item_cf_top_n_recommendation_map.xlsx")
    # item_cf.get_top_n()
    # print(item_cf.run("109087"))

    user_cf = UserCF(mydb, "user_cf_top_n_recommendation_map.feather")
    user_cf.get_top_n()
    # ic(user_cf.run("109087"))

    # hybrid_cf = HybridCF(mydb, "hybrid_cf_top_n_recommendation_map.feather")
    # hybrid_cf.get_top_n()
    # ic(len(hybrid_cf.run("128956")))
    # ic(len(set(hybrid_cf.run("128956"))))



