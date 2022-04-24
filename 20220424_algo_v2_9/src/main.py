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
    # param, hybridCF_fscores = algos.hybridCF_tuning(np.arange(0.4, 0.6, 0.02))

    # visualization.itemCF_tuning_vis()
    # visualization.userCF_tuning_vis()

    # iteration = 20
    # arr = np.zeros(iteration, dtype=float)
    # for i in range(iteration):
    #     arr[i] = algos.calc_train_test_ratio()
    # print(np.average(arr))

    # algos.store_metrics_of_all_algos(10)

    item_cf_params = np.load(os.path.join(configs.tuning_result_folder_path, "item_cf_params.npy"))
    item_cf = UserCF(mydb,
                     "item_cf_top_n_recommendation_map.xlsx",
                     item_cf_params[0],
                     item_cf_params[1]
                     )
    item_cf.get_top_n()
    print(item_cf.run("49070"))

    user_cf_params = np.load(os.path.join(configs.tuning_result_folder_path, "user_cf_params.npy"))
    user_cf = UserCF(mydb,
                     "user_cf_top_n_recommendation_map.xlsx",
                     user_cf_params[0],
                     user_cf_params[1]
                     )
    user_cf.get_top_n()
    print(user_cf.run("49070"))
    #
    # hybrid_cf = HybridCF(mydb,
    #                      "item_cf_in_hybrid_cf_top_n_recommendation_map.feather",
    #                      "user_cf_in_hybrid_cf_top_n_recommendation_map.feather",
    #                      )
    # print(hybrid_cf.run("49070"))
