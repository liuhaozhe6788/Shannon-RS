# encoding:utf-8
import os
import pandas as pd

import configs
import database
import visualization
import utils
from algo_list import run_all_users


if __name__ == "__main__":
    visualization.cleaned_data_vis("data_20220222.xlsx")

    mydb = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))


    # visualization.club_dist_vis(gama_df, mydb)
    # visualization.accu_vis(gama_df, mydb)
