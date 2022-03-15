# encoding:utf-8
import os
import numpy as np
import pandas as pd
import random
from icecream import ic

import configs
import database
import utils
import algo_list.generalized_cf
import algo_list.item_cf


# 将database中的点赞行为数据划分为训练集和测试集
def _train_test_split(data_base_, train_ratio=0.5):
    for usr in data_base_.like_users:
        like_items = data_base_.get_objs(['user', usr, 'like', 'item'], key="动态")
        like_indices = len(like_items)
        train_indices = sorted(random.sample(range(like_indices), k=int(train_ratio * like_indices)))
        test_indices = [i for i in range(like_indices) if i not in train_indices]
        train_like_items = [like_items[i] for i in train_indices]
        test_like_items = [like_items[i] for i in test_indices]
        yield [usr, train_like_items, test_like_items]


# 使用训练集的数据训练模型，得到推荐结果
def _get_recommendation(data_base_, algo_name, item_category="动态"):
    _train_test_split(data_base_, train_ratio=0.5)
    if item_category == "动态":
        recommend_data = []
        train_data = []
        test_data = []

        for usr, train_like_items, test_like_items in _train_test_split(data_base_, train_ratio=0.5):
            train_data.append((usr, train_like_items))
            for test_like_item in test_like_items:
                test_data.append([usr, test_like_item])
        train_data = dict(train_data)

        if algo_name == "item_cf":
            algo_list.item_cf.get_top_n(data_base_, train_data, test_flag=True)

        for usr in data_base_.like_users:
            if algo_name == "generalized_cf":
                gama = algo_list.generalized_cf.run_generalized_cf(usr, data_base_, train_data, test_flag=True)
                for recommend_item in gama:
                    recommend_data.append([usr, recommend_item])
            elif algo_name == "item_cf":
                gama = algo_list.item_cf.run_item_cf(usr, data_base_, train_data, test_flag=True)
                for recommend_item in gama:
                    recommend_data.append([usr, recommend_item])
        test_df = pd.DataFrame(data=test_data)
        test_df = test_df.rename(columns={0: "user", 1: "item"})
        recommend_df = pd.DataFrame(data=recommend_data)
        recommend_df = recommend_df.rename(columns={0: "user", 1: "item"})
    return test_df, recommend_df


# 使用测试集的数据进行推荐精度、命中率/召回率和F-score的计算
def calc_metrics(data_base_, algo_name):
    test_df, recommend_df = _get_recommendation(data_base_, algo_name, item_category="动态")
    # ic(test_df.head())
    # ic(recommend_df.head())
    tp_df = pd.merge(test_df, recommend_df, on=["user", "item"])
    accuracy_ = len(tp_df)/len(recommend_df)
    hit_ratio_ = len(tp_df)/len(test_df)
    f_score_ = 2 * accuracy_ * hit_ratio_/(accuracy_ + hit_ratio_)
    return [accuracy_, hit_ratio_, f_score_]


def store_metrics(num_iter):
    utils.create_folder_paths()
    db = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    item_cf_metrics_data = [[], [], []]
    generalized_cf_metrics_data = [[], [], []]
    for i in range(num_iter):
        [accuracy, hit_ratio, f_score] = calc_metrics(db, algo_name="item_cf")
        item_cf_metrics_data[0].append(accuracy)
        item_cf_metrics_data[1].append(hit_ratio)
        item_cf_metrics_data[2].append(f_score)

        [accuracy, hit_ratio, f_score] = calc_metrics(db, algo_name="generalized_cf")
        generalized_cf_metrics_data[0].append(accuracy)
        generalized_cf_metrics_data[1].append(hit_ratio)
        generalized_cf_metrics_data[2].append(f_score)

    item_cf_metrics_df = pd.DataFrame(data=item_cf_metrics_data)
    item_cf_metrics_df["mean"] = item_cf_metrics_df.mean(axis=1)
    item_cf_metrics_df["std"] = item_cf_metrics_df.std(axis=1)
    # ic(item_cf_metrics_df)

    generalized_cf_metrics_df = pd.DataFrame(data=generalized_cf_metrics_data)
    generalized_cf_metrics_df["mean"] = generalized_cf_metrics_df.mean(axis=1)
    generalized_cf_metrics_df["std"] = generalized_cf_metrics_df.std(axis=1)
    # ic(generalized_cf_metrics_df)

    item_cf_metrics_df.to_excel(os.path.join(configs.perf_result_folder_path, "item_cf.xlsx"))
    generalized_cf_metrics_df.to_excel(os.path.join(configs.perf_result_folder_path, "generalized_cf.xlsx"))


if __name__ == "__main__":
    utils.create_folder_paths()
    # db = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    # for i in range(10):
    #     db = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    #     [accuracy, hit_ratio, f_score] = calc_metrics(db, algo_name="item_cf")
    #     ic([accuracy, hit_ratio, f_score])
    #     [accuracy, hit_ratio, f_score] = calc_metrics(db, algo_name="generalized_cf")
    #     ic([accuracy, hit_ratio, f_score])
    store_metrics(20)
