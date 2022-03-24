# encoding:utf-8
import os
import random
import numpy as np
import pandas as pd
import feather
from sklearn.metrics.pairwise import pairwise_distances
from icecream import ic

import configs
import utils
from database import DataBase
np.set_printoptions(threshold=np.inf)


def _map_list_to_index(a: list) -> dict:
    return dict(zip(tuple(a), range(len(a))))


def _map_index_to_list(a: list) -> dict:
    return dict(zip(range(len(a)), tuple(a)))


def _create_ui_matrix(data_base_: DataBase, train_data=None, test_flag=False) -> np.ndarray:
    users = data_base_.like_users
    users_map = _map_list_to_index(users)
    dynamics = data_base_.liked_dynamics
    dynamics_map = _map_list_to_index(dynamics)
    ui_matrix = np.zeros((len(data_base_.like_users), len(data_base_.liked_dynamics)), dtype="float32")
    for u in users:
        if test_flag:
            like_items = train_data[str(u)]
        else:
            like_items = data_base_.get_objs(["user", u, 'like', 'item'], key="动态")
        # like_items_map = [dynamics_map[s] for s in like_items]
        for i in like_items:
            ui_matrix[users_map[u]][dynamics_map[i]] = 1
        # like_items_index = ui_matrix[users_map[u]][:].nonzero()
    return ui_matrix


def _calc_item_similarities(ui_matrix: np.ndarray) -> np.ndarray:
    item_similarities_ = pairwise_distances(ui_matrix.T, metric="cosine")
    item_similarities_ = np.ones(item_similarities_.shape) - item_similarities_
    return item_similarities_


def _predict(ui_matrix: np.ndarray, item_similarities_: np.ndarray) -> np.ndarray:
    pred = ui_matrix.dot(item_similarities_) / np.array([np.abs(item_similarities_).sum(axis=1)])
    return pred


def get_top_n(data_base_: DataBase, train_data=None, test_flag=False) -> list:
    """
    实现基于物品的协同过滤算法，并将所有用户的前N名推荐结果存入.feather文档
    :param data_base_:数据库类
    :param train_data:
    :param test_flag:
    :return:None
    """
    def _get_item_list(row, reverse_map, top_n=45):
        items = [reverse_map[i] for i in list(row[: -1])]
        if test_flag:
            like_items = train_data[str(row["user"])]
        else:
            like_items = data_base_.get_objs(["user", str(row["user"]), 'like', 'item'], key="动态")
        view_items = data_base_.get_objs(['user', str(row["user"]), 'view', 'item'], key="动态")
        create_items = data_base_.get_objs(['user', str(row["user"]), 'create', 'item'], key="动态")
        items = [i for i in items if(i not in like_items) and (i not in view_items) and (i not in create_items)]
        return items[: top_n]
    users = data_base_.like_users
    # users_map = _map_list_to_index(users)
    users_reverse_map = _map_index_to_list(users)
    dynamics = data_base_.liked_dynamics
    dynamics_reverse_map = _map_index_to_list(dynamics)

    ui_matrix = _create_ui_matrix(data_base_, train_data, test_flag=False)
    item_similarities_ = _calc_item_similarities(ui_matrix)
    pred = _predict(ui_matrix, item_similarities_)

    sorted_items = np.argsort(-pred)  # 根据pred，对每个用户的物品进行降序排序
    df = pd.DataFrame(data=sorted_items)
    df["user"] = np.arange(len(df))
    df["user"] = df.apply(lambda x: users_reverse_map[x["user"]], axis=1)  # 根据行索引增加用户栏
    cols = df.columns
    top_n = 45
    df["top_n"] = df.apply(lambda x: _get_item_list(x[cols], dynamics_reverse_map, top_n), axis=1)  # 获得每位用户的top45物品列表
    # df["items_len"] = df.apply(lambda x: len(x["top_n"].split(",")), axis=1)
    # ic(df[df["items_len"] != 45])

    top_n_df = df[["user", "top_n"]]
    feather.write_dataframe(top_n_df, os.path.join(configs.rec_result_folder_path, "item_cf_top_n_recommendation_map.feather"))
    return None


def run_item_cf(user_id, data_base_, train_data=None, test_flag=False):
    """
    对user_id用户进行物品推荐，该过程读取.feather文档，找到用户对应的前N名物品随后增加最受欢迎的物品
    :param user_id:
    :param data_base_:
    :param train_data:
    :param test_flag:
    :return:
    """
    top_n_df = feather.read_dataframe(os.path.join(configs.rec_result_folder_path, "item_cf_top_n_recommendation_map.feather"))
    top_n_items = list(list(top_n_df[top_n_df["user"] == str(user_id)]["top_n"])[0])
    # print(top_n_items)
    n_items = 50
    n_top_n = len(top_n_items)
    m = data_base_.get_objs(["club", "动态:推广集", "have", "selected_item"], key="动态")
    if test_flag:
        like_items = train_data[str(user_id)]
    else:
        like_items = data_base_.get_objs(["user", str(user_id), 'like', 'item'], key="动态")
    view_items = data_base_.get_objs(['user', str(user_id), 'view', 'item'], key="动态")
    create_items = data_base_.get_objs(['user', str(user_id), 'create', 'item'], key="动态")
    m = [i for i in m if (i not in like_items) and (i not in view_items) and (i not in create_items)]
    m_ = random.sample(list(m), k=n_items - n_top_n)
    gama = top_n_items + m_

    # gama = list(filter(lambda s: '剧本杀' in list(map(lambda x: x.split(":")[-2], data_base_.get_objs(['item', s, 'have', 'club'], key="动态"))), gama))
    n_gama = len(gama)

    if n_gama > n_items:
        raise ValueError(f"输出推荐集gama的长度错误，大于{n_items}")

    return data_base_.filter("动态", gama, del_prefix=False)


if __name__ == "__main__":
    utils.create_folder_paths()
    mydb = DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    get_top_n(mydb)
    ic(run_item_cf("49199", mydb))
