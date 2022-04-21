# encoding:utf-8
import os
import random
import numpy as np
import itertools
import sys

sys.dont_write_bytecode = True

import configs
import utils
from database import DataBase
from .generalized_cf import GeneralizedCF
from .user_cf import UserCF
from .basic import Basic

np.set_printoptions(threshold=np.inf)


class HybridCF():

    def __init__(self, database, buffer_name, p=0.6, train_data=None, test_flag=False, filter_flag=True):
        self.database = database
        self.p = p
        self.buffer_name = buffer_name
        self.train_data = train_data
        self.test_flag = test_flag
        self.filter_flag = filter_flag
        self.user_cf_params = np.load(os.path.join(configs.perf_result_folder_path, "user_cf_params.npy"))
        self.user_cf = UserCF(database, buffer_name, self.user_cf_params[0], self.user_cf_params[1], train_data, test_flag, filter_flag)
        self.generalized_cf = GeneralizedCF(self.database, self.train_data, self.test_flag, self.filter_flag)
        self.basic = Basic(database)

    def get_top_n(self):
        self.user_cf.get_top_n()

    def run(self, usr):
        """
        对user_id用户进行物品推荐，该过程读取.feather文档，找到用户对应的前N名物品随后增加最受欢迎的物品
        :param usr:
        :return:
        """
        max_length_of_rec = 50
        user_cf_items = self.user_cf.run(usr)
        num_user_cf_items = len(user_cf_items)
        k = int(max_length_of_rec * self.p)
        user_cf_items = user_cf_items[: min(k, num_user_cf_items)]
        num_user_cf_items = len(user_cf_items)

        generalized_cf_items = self.generalized_cf.run(usr)
        num_generalized_cf_items = len(generalized_cf_items)
        generalized_cf_items = generalized_cf_items[: min(int(max_length_of_rec * (1 - self.p)), num_generalized_cf_items)]
        num_generalized_cf_items = len(generalized_cf_items)

        gama = list(itertools.chain(*zip(user_cf_items, generalized_cf_items)))

        if num_user_cf_items <= num_generalized_cf_items:
            gama += generalized_cf_items[num_user_cf_items: ]
        else:
            gama += user_cf_items[num_generalized_cf_items: ]

        gama = list(dict.fromkeys(gama))
        gama = gama[: min(len(gama), max_length_of_rec)]

        return self.database.filter("动态", gama, del_prefix=False)


if __name__ == "__main__":
    utils.create_folder_paths()
    db = DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
