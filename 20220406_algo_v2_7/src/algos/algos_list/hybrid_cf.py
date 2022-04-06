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

    def __init__(self, database, buffer_name, train_data=None, test_flag=False, filter_flag=True):
        self.database = database
        self.buffer_name = buffer_name
        self.train_data = train_data
        self.test_flag = test_flag
        self.filter_flag = filter_flag
        self.user_cf = UserCF(database, buffer_name, train_data, test_flag, filter_flag)
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
        user_cf_items = self.user_cf.run(usr)

        generalized_cf_items = self.generalized_cf.run(usr)

        gama = list(itertools.chain(*zip(user_cf_items, generalized_cf_items)))

        gama = list(dict.fromkeys(gama))[: 50]

        return self.database.filter("动态", gama, del_prefix=False)


if __name__ == "__main__":
    utils.create_folder_paths()
    db = DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    hybrid_cf = HybridCF("50121", db)
    print(len(hybrid_cf.run()))
