# encoding:utf-8
import os
import pandas as pd

import configs
import database
import visualization
import utils
from algo_list import run_all


if __name__ == "__main__":
    visualization.cleaned_data_vis("data_20220222.xlsx")

    mydb = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))

    utils.create_folder_paths()
    algo_name = "item_cf"
    gama_df = run_all(mydb, algo_name)
    visualization.club_dist_vis(gama_df, mydb)
    # visualization.accu_vis(gama_df, mydb)
