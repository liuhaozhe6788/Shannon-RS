# encoding:utf-8
import os
import pandas as pd
import sys
sys.dont_write_bytecode = True

import configs
import database
import utils
import algo_list.generalized_cf
import algo_list.item_cf


def run_all_users(data_base_, algo_name, item_category="动态"):
    """
    对所有点赞用户做推荐，推荐结果存储在.xlsx表格中
    :param data_base_:数据库类
    :param algo_name:算法名称
    :param item_category:物品类别，默认为动态
    :return:所有用户的推荐结果
    """
    if item_category == "动态":
        gama_sets = []

        if algo_name == "item_cf":
            algo_list.item_cf.get_top_n(data_base_)

        for usr in data_base_.like_users:
            if algo_name == "generalized_cf":
                gama = algo_list.generalized_cf.run_generalized_cf(usr, data_base_)
            elif algo_name == "item_cf":
                gama = algo_list.item_cf.run_item_cf(usr, data_base_)
            gama_sets.append(",".join(gama))
        # print(dict(zip(data_base_.like_users, gama_sets)))
        gama_df = pd.DataFrame(data={"user": data_base_.like_users, "recommendation": gama_sets})
        gama_df.to_excel(os.path.join(configs.rec_result_folder_path, f"{algo_name}_recommendation_map.xlsx"), index=False)
        gama_df["recommendation"] = gama_df.apply(lambda x: x["recommendation"].split(","), axis=1)
        return gama_df


def run_all_algos(db_):
    utils.create_folder_paths()
    item_cf_res = run_all_users(db_, "item_cf")
    generalized_cf_res = run_all_users(db_, "generalized_cf")
    return [generalized_cf_res, item_cf_res]


if __name__ == "__main__":
    utils.create_folder_paths()
    db = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    generalized_cf_res, item_cf_res = run_all_algos(db)
    print(list(generalized_cf_res.loc[generalized_cf_res["user"] == "49070", "recommendation"])[0])
