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
from .basic import Basic
np.set_printoptions(threshold=np.inf)


class ItemCF():

    def __init__(self, database, train_data=None, test_flag=False, filter_flag=True):
        self.usr = None
        self.database = database
        self.train_data = train_data
        self.test_flag = test_flag
        self.filter_flag = filter_flag
        self.like_users = self.database.like_users
        self.liked_dynamics = self.database.liked_dynamics
        self.like_users_map = self.map_list_to_index(self.like_users)
        self.liked_dynamics_map = self.map_list_to_index(self.liked_dynamics)
        self.like_users_reverse_map = self.map_index_to_list(self.like_users)
        self.liked_dynamics_reverse_map = self.map_index_to_list(self.liked_dynamics)
        self.basic = Basic(self.database)

    @staticmethod
    def map_list_to_index(a: list) -> dict:
        return dict(zip(tuple(a), range(len(a))))

    @staticmethod
    def map_index_to_list(a: list) -> dict:
        return dict(zip(range(len(a)), tuple(a)))

    def create_ui_matrix(self) -> np.ndarray:
        ui_matrix = np.zeros((len(self.like_users), len(self.liked_dynamics)), dtype="float32")
        for u in self.like_users:
            if self.test_flag:
                like_items = self.train_data[str(u)]
            else:
                like_items = self.database.get_objs(["user", u, 'like', 'item'], key="动态")
            # like_items_map = [dynamics_map[s] for s in like_items]
            for i in like_items:
                ui_matrix[self.like_users_map[u]][self.liked_dynamics_map[i]] = 1
            # like_items_index = ui_matrix[users_map[u]][:].nonzero()
        return ui_matrix

    @staticmethod
    def calc_item_similarities(ui_matrix: np.ndarray) -> np.ndarray:
        item_similarities_ = pairwise_distances(ui_matrix.T, metric="cosine")
        item_similarities_ = np.ones(item_similarities_.shape) - item_similarities_
        return item_similarities_

    @staticmethod
    def predict(ui_matrix: np.ndarray, item_similarities_: np.ndarray) -> np.ndarray:
        pred = ui_matrix.dot(item_similarities_) / np.array([np.abs(item_similarities_).sum(axis=0)])
        return pred

    def get_top_n(self):
        """
        实现基于物品的协同过滤算法，并将所有用户的前N名推荐结果存入.feather文档
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
        item_similarities_ = self.calc_item_similarities(ui_matrix)
        pred = self.predict(ui_matrix, item_similarities_)

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
        feather.write_dataframe(top_n_df, os.path.join(configs.rec_result_folder_path,
                                                       "item_cf_top_n_recommendation_map.feather"))
        return None

    def run(self, usr):
        """
        对user_id用户进行物品推荐，该过程读取.feather文档，找到用户对应的前N名物品随后增加最受欢迎的物品
        :param usr:
        :return:
        """
        self.usr = usr
        top_n_df = feather.read_dataframe(os.path.join(configs.rec_result_folder_path,
                                                       "item_cf_top_n_recommendation_map.feather"))
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
    item_cf = ItemCF(mydb)
    item_cf.get_top_n()
    ic(item_cf.run("49199"))
