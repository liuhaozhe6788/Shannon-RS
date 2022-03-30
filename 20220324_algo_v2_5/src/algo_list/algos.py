# encoding:utf-8
import pandas as pd
import os
import sys

import utils
import configs
from database import DataBase
from generalized_cf import GeneralizedCF
sys.dont_write_bytecode = True


class Algos(object):
    """
        运行所有推荐算法和计算推荐算法的性能指标
    """

    def __init__(self, algo_names, database):
        self.__algo_names = algo_names
        self.__database = database
        utils.create_folder_paths()

    def run_all_algos(self) -> list:
        """
        运行所有推荐算法得到推荐结果
        :return: 推荐结果列表，列表元素为一个推荐算法给所有用户的推荐结果为pd.DataFrame型
        """
        algo_res_list = []
        for algo_name in self.__algo_names:
            res = self.run_all_users(algo_name)
            algo_res_list.append(res)
        return algo_res_list

    def run_all_users(self, algo_name, item_cat="动态"):
        """
        对所有点赞用户做推荐，推荐结果存储在.xlsx表格中
        :param algo_name:算法名称
        :param item_cat:物品类别，默认为动态
        :return:所有用户的推荐结果
        """
        if item_cat == "动态":
            gama_sets = []
            #
            # if algo_name == "item_cf":
            #     algo_list.item_cf.get_top_n(data_base_)

            for usr in self.__database.like_users:
                if algo_name == "generalized_cf":
                    generalized_cf = GeneralizedCF(usr, self.__database)
                    gama = generalized_cf.run_generalized_cf()
                # elif algo_name == "item_cf":
                #     gama = algo_list.item_cf.run_item_cf(usr, data_base_)
                gama_sets.append(",".join(gama))
            # print(dict(zip(data_base_.like_users, gama_sets)))
            gama_df = pd.DataFrame(data={"user": self.__database.like_users, "recommendation": gama_sets})
            gama_df.to_excel(os.path.join(configs.rec_result_folder_path, f"{algo_name}_recommendation_map.xlsx"),
                             index=False)
            gama_df["recommendation"] = gama_df.apply(lambda x: x["recommendation"].split(","), axis=1)
            return gama_df


if __name__ == "__main__":
    utils.create_folder_paths()
    db = DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    algos = Algos(["generalized_cf"], db)
    generalized_cf_res = algos.run_all_algos()[0]


