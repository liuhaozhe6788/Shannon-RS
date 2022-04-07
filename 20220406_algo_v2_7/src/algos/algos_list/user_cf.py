# encoding:utf-8
import os
import random
import numpy as np
import pandas as pd
import feather
from sklearn.metrics.pairwise import pairwise_distances
from icecream import ic
import sys
sys.dont_write_bytecode = True

import configs
import utils
from database import DataBase
from .item_cf import ItemCF
np.set_printoptions(threshold=np.inf)


class UserCF(ItemCF):

    def __init__(self, database, buffer_name, train_data=None, test_flag=False, filter_flag=True):

        super().__init__(database, buffer_name, train_data, test_flag, filter_flag)

    @staticmethod
    def calc_user_similarities(ui_matrix: np.ndarray) -> np.ndarray:
        user_similarities_ = pairwise_distances(ui_matrix, metric="cosine")
        user_similarities_ = np.ones(user_similarities_.shape) - user_similarities_
        return user_similarities_

    @staticmethod
    def predict(ui_matrix: np.ndarray, user_similarities_: np.ndarray) -> np.ndarray:
        mean_user_rating = ui_matrix.mean(axis=1)
        ratings_diff = ui_matrix - mean_user_rating[:, np.newaxis]
        pred = mean_user_rating[:, np.newaxis] + user_similarities_.dot(ratings_diff)/ np.array([np.abs(user_similarities_).sum(axis=1)]).T
        return pred

    def get_top_n(self):
        """
        实现基于用户的协同过滤算法，并将所有用户的前N名推荐结果存入.feather文档
        :return:None
        """

        def _get_item_list(row, reverse_map):
            items = [reverse_map[i] for i in list(row[: -1])]
            if self.test_flag:
                like_items = self.train_data[str(row["user"])]
            else:
                like_items = self.database.get_objs(["user", str(row["user"]), 'like', 'item'], key="动态")
            view_items = self.database.get_objs(['user', str(row["user"]), 'view', 'item'], key="动态")
            create_items = self.database.get_objs(['user', str(row["user"]), 'create', 'item'], key="动态")
            items = [i for i in items if (i not in like_items) and (i not in view_items) and (i not in create_items)]
            return ",".join(items)

        ui_matrix = self.create_ui_matrix()
        user_similarities_ = self.calc_user_similarities(ui_matrix)
        pred = self.predict(ui_matrix, user_similarities_)

        sorted_items = np.argsort(-pred)  # 根据pred，对每个用户的物品进行降序排序
        df = pd.DataFrame(data=sorted_items)
        df["user"] = np.arange(len(df))
        df["user"] = df["user"].apply(lambda x: self.like_users_reverse_map[x])  # 根据行索引增加用户栏
        cols = df.columns
        df["top_n"] = df.apply(lambda x: _get_item_list(x[cols], self.liked_dynamics_reverse_map),
                               axis=1)  # 获得每位用户的top_n物品列表

        # df["items_len"] = df.apply(lambda x: len(x["top_n"].split(",")), axis=1)
        # ic(df[df["items_len"] != 45])

        top_n_df = df[["user", "top_n"]]
        top_n_df = top_n_df.astype({"user": str})
        feather.write_dataframe(top_n_df, os.path.join(configs.buffer_files_folder_path,
                                                       self.buffer_name))
        return None

    def run(self, usr):
        """
        对user_id用户进行物品推荐，该过程读取.feather文档，找到用户对应的前N名物品随后增加最受欢迎的物品
        :param usr:
        :return:
        """
        self.usr = usr
        top_n_df = feather.read_dataframe(os.path.join(configs.buffer_files_folder_path,
                                                       self.buffer_name))
        top_n_df = top_n_df.astype({"user": str})
        if top_n := list(top_n_df[top_n_df["user"] == str(self.usr)]["top_n"]):
            top_n_items = top_n[0].split(",")
        else:
            top_n_items = []

        if self.filter_flag:
            top_n_items = self.basic.filter_club(top_n_items, "剧本杀")

        gama, n_gama = self.basic.rearrangement(top_n_items, len(top_n_items), self.usr, self.train_data, self.test_flag, self.filter_flag)

        return self.database.filter("动态", gama, del_prefix=False)


if __name__ == "__main__":
    utils.create_folder_paths()
    mydb = DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    user_cf = UserCF(mydb)
    user_cf.get_top_n()
    ic(user_cf.run("49199"))
