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
    # algos.store_metrics(50)
    # iteration = 20
    # arr = np.zeros(iteration, dtype=float)
    # for i in range(iteration):
    #     arr[i] = algos.calc_train_test_ratio()
    # ic(np.average(arr))


    # item_cf = ItemCF(mydb, "item_cf_top_n_recommendation_map.xlsx")
    # item_cf.get_top_n()
    # ic(item_cf.run("109087"))

    user_cf = UserCF(mydb, "user_cf_top_n_recommendation_map.feather")
    user_cf.get_top_n()
    ic(user_cf.run("109087"))

    # hybrid_cf = HybridCF(mydb, "hybrid_cf_top_n_recommendation_map.feather")
    # hybrid_cf.get_top_n()
    # ic(len(hybrid_cf.run("128956")))
    # ic(len(set(hybrid_cf.run("128956"))))



