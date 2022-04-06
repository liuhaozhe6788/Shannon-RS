# encoding:utf-8
import os
import pandas as pd
import sys
sys.dont_write_bytecode = True

import configs
import database
import visualization
from algos import AlgosOperator
import utils


if __name__ == "__main__":
    # visualization.cleaned_data_vis("data_20220222.xlsx")

    mydb = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))

    algos = AlgosOperator(mydb)
    algos.calc_and_store_metrics(3)
    algos.calc_and_store_metrics(3)

