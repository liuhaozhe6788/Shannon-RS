# encoding:utf-8
import os

import numpy as np
import pandas as pd
import PIL
import requests
import io
from icecream import ic
import sys
sys.dont_write_bytecode = True

import configs
from algo_list import run_all_users
import database
import plotting
import utils


def _save_imgs(img_urls, folder_path, img_names):
    """
    存储图片到对应文件夹中
    :param img_urls:
    :param folder_path:
    :param img_names:
    :return:
    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    for k in range(len(img_urls)):
        response = requests.get(img_urls[k])
        image_bytes = io.BytesIO(response.content)

        img = PIL.Image.open(image_bytes)
        # img.show()
        img.save(os.path.join(folder_path, f"{img_names[k].split(':')[-1]}.png"))


def _freq_calc(items, clubs_list, n_clubs, data_base_) -> (np.ndarray, list, list):
    """
    计算某个物品集的出现的CLUB标签频率
    :param items:某个物品集
    :param clubs_list:CLUB标签列表
    :param n_clubs:CLUB标签总个数
    :param data_base_:DataBase类的实例
    :return: CLUB标签在某个物品集出现的频率
    """
    frequencies = np.zeros(n_clubs, dtype=float)
    for it in items:
        clubs_of_item = list(map(lambda x: ":".join(x.split(":")[:-1]), data_base_.get_objs(['item', it, 'have', 'club'], key="动态")))
        for c in clubs_of_item:  # 一个动态可能属于多个标签
            club_label = c.split(":")[-1]
            frequencies[clubs_list.index(club_label)] += 1 / len(clubs_of_item)
    # ic(frequencies.sum())
    frequencies /= frequencies.sum()

    # if len(img_urls) == 0:
    #     print("由于该CLUB标签的推荐物品都没有图片信息，故展示物品的文本内容")
    #     for it in items:
    #         clubs_of_item = data_base_.get_objs(['item', it, 'have', 'club'], key="动态")
    #         for c in clubs_of_item:
    #             club_label = c.split(":")[-1].split("_")[0]
    #             if club_label == default_label:
    #                 print(f"{it}:")
    #                 print(data_base_.get_objs(['item', it, 'have', 'content_text']))

    return frequencies


def accu_vis(algo_name, gama_result, data_base_):
    """
    所有CLUB标签的推荐精度计算与可视化
    一个CLUB标签c的推荐精度的计算：
    推荐集中CLUB标签c出现次数最高且点赞物品中CLUB标签c出现次数最高的所有用户数/点赞物品中CLUB标签c出现次数最高的所有用户数
    :param algo_name:算法名称
    :param gama_result:所有用户的推荐结果
    :param data_base_:DataBase类的实例
    :return: None
    """
    clubs_list = list(dict.fromkeys(list(map(lambda x: x.split(":")[-2], list(filter(lambda s: s.startswith("动态"), data_base_.clubs))))))
    n_clubs = len(clubs_list)
    like_occurence = np.zeros(n_clubs, dtype=int)
    accur_occurence = np.zeros(n_clubs, dtype=int)

    for usr in data_base_.like_users:
        user_like = data_base_.get_objs(['user', usr, 'like', 'item'], key="动态")
        n_user_like = len(user_like)
        n_recently_like = 300
        n_recently_like = min(n_recently_like, n_user_like)
        user_like_freq = _freq_calc(user_like[-n_recently_like:], clubs_list, n_clubs, data_base_)

        gama = list(gama_result[gama_result["user"] == str(usr)]["recommendation"])[0]
        # print(gama)
        gama_freq = _freq_calc(gama, clubs_list, n_clubs, data_base_)

        user_like_club_max = np.where(user_like_freq == np.amax(user_like_freq))
        gama_club_max = np.where(gama_freq == np.amax(gama_freq))
        like_occurence[user_like_club_max] += 1
        accur_occurence[np.intersect1d(user_like_club_max, gama_club_max)] += 1

    # ic(accur_occurence, like_occurence, like_occurence.shape)
    # ic(like_occurence.nonzero())

    nonzero_ids = like_occurence.nonzero()
    accur_occurence = accur_occurence[nonzero_ids]
    like_occurence = like_occurence[nonzero_ids]
    clubs_list = list(np.array(clubs_list)[nonzero_ids])
    n_clubs = len(clubs_list)

    # ic(accur_occurence, like_occurence, clubs_list)

    accuracies = np.zeros(n_clubs, dtype=float)
    np.divide(accur_occurence, like_occurence, accuracies)

    my_plot = plotting.PlotGenerator()
    df = pd.DataFrame({
        "x_values": clubs_list * 1,
        "freq": np.concatenate(accuracies, axis=None),
        "cat": [algo_name] * len(accuracies)
    })
    # print(df)
    my_plot.bar_plot(x="x_values",
                     y="freq",
                     hue="cat",
                     data=df,
                     figwidth=45,
                     figheight=10,
                     new_xticks=list(map(lambda x: x[:5] + "\n" + x[5:] if len(x) > 5 else x, clubs_list)),
                     new_legend_labels=[f'算法{algo_name}的推荐性能'],
                     new_xlabel="CLUB标签",
                     new_ylabel="精度",
                     new_title=f"算法{algo_name}的推荐性能",
                     new_fig_name=os.path.join(configs.perf_result_folder_path, f"{algo_name}_accu_results.png"),
                     savefig=True
                     )


def club_dist_vis(algo_name, gama_result, data_base_):
    """
    点赞数最多的前3位用户的点赞物品与推荐集在CLUB标签分布的可视化
    :param algo_name:算法名称
    :param gama_result:所有用户的推荐结果
    :param data_base_:DataBase类的实例
    :return: None
    """
    clubs_list = list(dict.fromkeys(list(map(lambda x: x.split(":")[-2], list(filter(lambda s: s.startswith("动态"), data_base_.clubs))))))
    n_clubs = len(clubs_list)
    # print(clubs_list)

    # selected_users = random.choices(data_base_.users, k=3)
    selected_users = [49070, 48449, 48493]

    my_plot = plotting.PlotGenerator()
    dfs = []
    new_titles = []
    for k in range(len(selected_users)):
        user_view = data_base_.get_objs(['user', selected_users[k], 'view', 'item'], key="动态")
        n_user_view = len(user_view)
        n_recently_view = 300
        n_recently_view = min(n_recently_view, n_user_view)

        user_like = data_base_.get_objs(['user', selected_users[k], 'like', 'item'], key="动态")
        n_user_like = len(user_like)
        n_recently_like = 300
        n_recently_like = min(n_recently_like, n_user_like)

        if n_recently_view > 0:
            user_view_freq = _freq_calc(user_view[-n_recently_view:], clubs_list, n_clubs, data_base_)

        if n_recently_like > 0:
            user_like_freq = _freq_calc(user_like[-n_recently_like:], clubs_list, n_clubs, data_base_)

        gama = list(gama_result[gama_result["user"] == str(selected_users[k])]["recommendation"])[0]
        gama_freq = _freq_calc(gama, clubs_list, n_clubs, data_base_)

        df = pd.DataFrame({
            "x_values": clubs_list * 2,
            "freq": np.concatenate((user_like_freq, gama_freq), axis=None),
            "cat": ["user_like_freq"] * len(user_like_freq) + ["gama_freq"] * len(user_like_freq)
        })
        # print(df)
        dfs.append(df)
        new_titles.append(f"用户{selected_users[k]}的推荐动态与点赞动态的比较")
    my_plot.bar_plots(x="x_values",
                      y="freq",
                      hue="cat",
                      data=dfs,
                      figwidth=45,
                      figheight=10*len(selected_users),
                      new_xticks=list(map(lambda x: x[:5] + "\n" + x[5:] if len(x) > 5 else x, clubs_list)),
                      new_legend_labels=[f'用户点赞动态中{n_clubs}个club标签的频率', f'推荐集中{n_clubs}个club标签的频率'],
                      new_xlabel="CLUB标签",
                      new_ylabel="频率",
                      new_titles=new_titles,
                      new_fig_name=os.path.join(configs.perf_result_folder_path, f"{algo_name}_selected_results.png"),
                      savefig=True
                      )


if __name__ == "__main__":
    utils.create_folder_paths()

    mydb = database.DataBase(os.path.join(configs.data_folder_path, "data_20220222.xlsx"))
    algo_name = "item_cf"
    gama_df = run_all_users(mydb, algo_name)
    club_dist_vis(algo_name, gama_df, mydb)
    accu_vis(algo_name, gama_df, mydb)

    algo_name = "generalized_cf"
    gama_df = run_all_users(mydb, algo_name)
    club_dist_vis(algo_name, gama_df, mydb)
    accu_vis(algo_name, gama_df, mydb)
