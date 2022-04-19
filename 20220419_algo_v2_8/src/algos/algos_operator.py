# encoding:utf-8
import pandas as pd
import os
import sys
import random
from icecream import ic

import utils
import configs
from database import DataBase
from .algos_list import GeneralizedCF, ItemCF, UserCF, HybridCF, Basic
sys.dont_write_bytecode = True

random.seed(10)

class AlgosOperator(object):
    """
        运行所有推荐算法和计算推荐算法的性能指标
    """

    def __init__(self, database, filter_flag=True):
        self.database = database
        self.filter_flag = filter_flag
        self.basic = Basic(self.database)
        utils.create_folder_paths()

    def run_all_algos(self) -> list:
        """
        运行所有推荐算法得到推荐结果
        :return: 推荐结果列表，列表元素为一个推荐算法给所有用户的推荐结果为pd.DataFrame型
        """
        algo_res_list = []
        for algo_name in ['generalized_cf', 'item_cf', 'user_cf', 'hybrid_cf']:
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

            if algo_name == "generalized_cf":
                generalized_cf = GeneralizedCF(self.database)
                for usr in self.database.like_users:
                    gama = generalized_cf.run(usr)
                    gama_sets.append(",".join(gama))

            elif algo_name == "item_cf":
                item_cf = ItemCF(self.database, "item_cf_top_n_recommendation_map.feather")
                item_cf.get_top_n()

                for usr in self.database.like_users:
                    gama = item_cf.run(usr)
                    gama_sets.append(",".join(gama))

            elif algo_name == "user_cf":
                user_cf = UserCF(self.database, "user_cf_top_n_recommendation_map.feather")
                user_cf.get_top_n()

                for usr in self.database.like_users:
                    gama = user_cf.run(usr)
                    gama_sets.append(",".join(gama))

            elif algo_name == "hybrid_cf":
                hybrid_cf = HybridCF(self.database, "hybrid_cf_top_n_recommendation_map.feather")
                hybrid_cf.get_top_n()
                for usr in self.database.like_users:
                    gama = hybrid_cf.run(usr)
                    gama_sets.append(",".join(gama))

            gama_df = pd.DataFrame(data={"user": self.database.like_users, "recommendation": gama_sets})
            gama_df.to_excel(os.path.join(configs.rec_result_folder_path, f"{algo_name}_recommendation_map.xlsx"),
                             index=False)
            gama_df["recommendation"] = gama_df.apply(lambda x: x["recommendation"].split(","), axis=1)
            return gama_df

    # 将database中的点赞行为数据划分为训练集和测试集
    def train_test_split(self, train_ratio=0.5):
        for usr in self.database.like_users:
            like_items = self.database.get_objs(['user', usr, 'like', 'item'], key="动态")
            like_indices = len(like_items)
            train_indices = sorted(random.sample(range(like_indices), k=int(train_ratio * like_indices) + 1))
            test_indices = [i for i in range(like_indices) if i not in train_indices]
            train_like_items = [like_items[i] for i in train_indices]
            test_like_items = [like_items[i] for i in test_indices]
            if self.filter_flag:
                test_like_items = self.basic.filter_club(test_like_items, "剧本杀")

            yield [usr, train_like_items, test_like_items]

    def calc_train_test_ratio(self):
        train_size = 0
        test_size = 0
        for usr, train_like_items, test_like_items in self.train_test_split(0.5):
            train_size += len(train_like_items)
            test_size += len(test_like_items)
        return train_size/test_size

    # 使用训练集的数据训练模型，得到推荐结果
    def get_recommendation(self, algo_name, item_category="动态"):
        if item_category == "动态":
            recommend_data = []
            train_data = []
            test_data = []

            for usr, train_like_items, test_like_items in self.train_test_split(0.5):
                train_data.append((usr, train_like_items))
                for test_like_item in test_like_items:
                    # if '剧本杀' in list(map(lambda x: x.split(":")[-2], data_base_.get_objs(['item', test_like_item, 'have', 'club'], key="动态"))):
                    test_data.append([usr, test_like_item])
            train_data = dict(train_data)

            if algo_name == "generalized_cf":
                for usr in self.database.like_users:
                    generalized_cf = GeneralizedCF(self.database, train_data=train_data, test_flag=True)
                    gama = generalized_cf.run(usr)
                    for recommend_item in gama:
                        recommend_data.append([usr, recommend_item])

            elif algo_name == "item_cf":
                item_cf_ = ItemCF(self.database, "item_cf_top_n_recommendation_map.feather", train_data=train_data, test_flag=True)
                item_cf_.get_top_n()

                for usr in self.database.like_users:
                    gama = item_cf_.run(usr)
                    for recommend_item in gama:
                        recommend_data.append([usr, recommend_item])

            elif algo_name == "user_cf":
                user_cf_ = UserCF(self.database, "user_cf_top_n_recommendation_map.feather", train_data=train_data, test_flag=True)
                user_cf_.get_top_n()

                for usr in self.database.like_users:
                    gama = user_cf_.run(usr)
                    for recommend_item in gama:
                        recommend_data.append([usr, recommend_item])

            elif algo_name == "hybrid_cf":
                hybrid_cf = HybridCF(self.database, "hybrid_cf_top_n_recommendation_map.feather", train_data=train_data, test_flag=True)
                hybrid_cf.get_top_n()

                for usr in self.database.like_users:
                    gama = hybrid_cf.run(usr)
                    for recommend_item in gama:
                        recommend_data.append([usr, recommend_item])

            test_df = pd.DataFrame(data=test_data)
            test_df = test_df.rename(columns={0: "user", 1: "item"})
            recommend_df = pd.DataFrame(data=recommend_data)
            recommend_df = recommend_df.rename(columns={0: "user", 1: "item"})
            return test_df, recommend_df
        else:
            return None

    # 使用测试集的数据进行推荐精度、命中率/召回率和F-score的计算
    def calc_metrics(self, algo_name):
        test_df, recommend_df = self.get_recommendation(algo_name, item_category="动态")
        # ic(test_df.head())
        # ic(recommend_df.head())
        tp_df = pd.merge(test_df, recommend_df, on=["user", "item"])
        accuracy_ = len(tp_df) / len(recommend_df)
        hit_ratio_ = len(tp_df) / len(test_df)
        # ic(len(tp_df), len(recommend_df), len(test_df))
        f_score_ = 2 * accuracy_ * hit_ratio_ / (accuracy_ + hit_ratio_)
        return [accuracy_, hit_ratio_, f_score_]

    def store_metrics(self, num_iter):
        generalized_cf_metrics_data = [[], [], []]
        item_cf_metrics_data = [[], [], []]
        user_cf_metrics_data = [[], [], []]
        hybrid_cf_metrics_data = [[], [], []]
        for i in range(num_iter):
            [accuracy, hit_ratio, f_score] = self.calc_metrics(algo_name="generalized_cf")
            generalized_cf_metrics_data[0].append(accuracy)
            generalized_cf_metrics_data[1].append(hit_ratio)
            generalized_cf_metrics_data[2].append(f_score)

            [accuracy, hit_ratio, f_score] = self.calc_metrics(algo_name="item_cf")
            item_cf_metrics_data[0].append(accuracy)
            item_cf_metrics_data[1].append(hit_ratio)
            item_cf_metrics_data[2].append(f_score)

            [accuracy, hit_ratio, f_score] = self.calc_metrics(algo_name="user_cf")
            user_cf_metrics_data[0].append(accuracy)
            user_cf_metrics_data[1].append(hit_ratio)
            user_cf_metrics_data[2].append(f_score)

            [accuracy, hit_ratio, f_score] = self.calc_metrics(algo_name="hybrid_cf")
            hybrid_cf_metrics_data[0].append(accuracy)
            hybrid_cf_metrics_data[1].append(hit_ratio)
            hybrid_cf_metrics_data[2].append(f_score)

        generalized_cf_metrics_df = pd.DataFrame(data=generalized_cf_metrics_data)
        generalized_cf_metrics_df["mean"] = generalized_cf_metrics_df.mean(axis=1)
        generalized_cf_metrics_df["std"] = generalized_cf_metrics_df.std(axis=1)
        ic(generalized_cf_metrics_df)

        item_cf_metrics_df = pd.DataFrame(data=item_cf_metrics_data)
        item_cf_metrics_df["mean"] = item_cf_metrics_df.mean(axis=1)
        item_cf_metrics_df["std"] = item_cf_metrics_df.std(axis=1)
        ic(item_cf_metrics_df)

        user_cf_metrics_df = pd.DataFrame(data=user_cf_metrics_data)
        user_cf_metrics_df["mean"] = user_cf_metrics_df.mean(axis=1)
        user_cf_metrics_df["std"] = user_cf_metrics_df.std(axis=1)
        ic(user_cf_metrics_df)

        hybrid_cf_metrics_df = pd.DataFrame(data=hybrid_cf_metrics_data)
        hybrid_cf_metrics_df["mean"] = hybrid_cf_metrics_df.mean(axis=1)
        hybrid_cf_metrics_df["std"] = hybrid_cf_metrics_df.std(axis=1)
        ic(hybrid_cf_metrics_df)

        generalized_cf_metrics_df.to_excel(os.path.join(configs.perf_result_folder_path, "generalized_cf.xlsx"))
        item_cf_metrics_df.to_excel(os.path.join(configs.perf_result_folder_path, "item_cf.xlsx"))
        user_cf_metrics_df.to_excel(os.path.join(configs.perf_result_folder_path, "user_cf.xlsx"))
        hybrid_cf_metrics_df.to_excel(os.path.join(configs.perf_result_folder_path, "hybrid_cf.xlsx"))


if __name__ == "__main__":
    db = DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    algos = AlgosOperator(db)
    # algos_list.run_all_algos()
    # algos.store_metrics(2)

