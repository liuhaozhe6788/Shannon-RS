# encoding:utf-8
import os
import numpy as np
import pandas as pd
import requests
import io
import shutil
from icecream import ic
import sys
sys.dont_write_bytecode = True

import configs
import random
import plotting
from database.preprocessing import clean_data
from database import DataBase


def cleaned_data_vis(cleaned_data_file):
    """
    对清洗的数据进行可视化
    :param cleaned_data_file: 清洗的数据的文档
    :return: None
    """
    cleaned_data_path = os.path.join(configs.data_folder_path, cleaned_data_file)
    user_df, item_df, club_df = clean_data(cleaned_data_path)

    if os.path.exists(configs.visualization_folder_path):
        shutil.rmtree(configs.visualization_folder_path)
    os.mkdir(configs.visualization_folder_path)

    plotgenerator = plotting.PlotGenerator()

    # print(user_df.head())
    # print(item_df.head())
    # print(club_df.head())

    # ic(user_df[(user_df["subject_id"] == 49070) & (user_df["behavior"] == "like")])

    # 用户数量、物品数量、点赞用户数量、不存在图片信息的剧本杀动态数量、点赞行为的数量、用户-物品点赞行为的稀疏度
    user_behaviors_df = user_df[user_df["behavior"].isin(["follow", "like", "view", "create", "join", "comment"])]
    users = user_behaviors_df["subject_id"].unique()
    ic(len(users))

    dynamics_item_df = item_df[item_df["content_type"].isin(["动态"])]
    dynamics_items = dynamics_item_df["item_id"]
    ic(len(dynamics_items))

    user_like_df = user_df[user_df["behavior"].isin(["like"])]
    like_users = user_like_df["subject_id"].unique()
    ic(like_users)
    liked_items = user_like_df["object_id"].unique()
    ic(len(liked_items))

    dynamics_item_df_ = dynamics_item_df.copy()
    dynamics_item_without_info_df_ = dynamics_item_df_[(dynamics_item_df_["image_url"] == "*") & (dynamics_item_df_["video_url"] == "*")]
    ic(len(dynamics_item_without_info_df_))  # 1个,但该动态未出现在用户行为数据中

    ic(len(user_like_df))

    data_sparsity = len(user_like_df)/(len(like_users)*len(liked_items))
    ic(data_sparsity)



    # 动态中所有club一级标签的数量分布，countplot
    dynamics_item_df_ = dynamics_item_df.copy()
    club_one_desc = dynamics_item_df_.apply(lambda x: x["item_desc"].split(":")[0], axis=1)
    club_one_desc = club_one_desc.to_frame().rename(columns={0: "desc"})
    # ic(club_one_desc)
    plotgenerator.count_plot(x="desc",
                             data=club_one_desc,
                             figwidth=60,
                             figheight=16,
                             new_xlabel="CLUB一级标签",
                             new_ylabel="动态的数量",
                             new_title="所有动态在CLUB一级标签的数量分布",
                             new_fig_name=os.path.join(configs.visualization_folder_path, f"num_of_items_per_club1_dist.png"),
                             savefig=True
                             )


    # # 动态中所有CLUB标签（剧本杀为二级标签，其他为一级标签）的数量分布，countplot
    # club_two_desc = dynamics_item_df_.apply(lambda x: x["item_desc"].split(":")[1] if (club1 := x["item_desc"].split(":")[0]) in ["剧本杀"] else club1, axis=1)
    # club_two_desc = club_two_desc.to_frame().rename(columns={0: "desc"})
    # club_two_desc["desc"] = club_two_desc.apply(lambda x: x["desc"][: 5] + "\n" + x["desc"][5: ] if len(x["desc"]) > 5 else x["desc"], axis=1)
    # # ic(club_two_desc)
    # plotgenerator.count_plot(x="desc",
    #                          data=club_two_desc,
    #                          figwidth=80,
    #                          figheight=28,
    #                          new_xlabel="CLUB标签（剧本杀为二级标签，其他为一级标签）",
    #                          new_ylabel="动态的数量",
    #                          new_title="所有动态在CLUB标签的数量分布",
    #                          new_fig_name=os.path.join(configs.visualization_folder_path, f"num_of_items_per_club2_dist.png"),
    #                          savefig=True
    #                          )

    like_df = user_df[user_df["behavior"] == "like"].copy()
    like_items = list(like_df["object_id"].unique())

    # 用户点赞动态中所有club一级标签的数量分布，countplot
    dynamics_item_df_ = dynamics_item_df.copy()
    dynamics_item_df_ = dynamics_item_df_[dynamics_item_df_["item_id"].isin(like_items)]
    club_one_desc = dynamics_item_df_.apply(lambda x: x["item_desc"].split(":")[0], axis=1)
    club_one_desc = club_one_desc.to_frame().rename(columns={0: "desc"})
    # ic(club_one_desc)
    plotgenerator.count_plot(x="desc",
                             data=club_one_desc,
                             figwidth=60,
                             figheight=16,
                             new_xlabel="CLUB一级标签",
                             new_ylabel="动态的数量",
                             new_title="用户点赞动态在CLUB一级标签的数量分布",
                             new_fig_name=os.path.join(configs.visualization_folder_path, f"num_of_like_items_per_club1_dist.png"),
                             savefig=True
                             )


    # # 用户点赞动态中所有CLUB标签（剧本杀为二级标签，其他为一级标签）的数量分布，countplot
    # club_two_desc = dynamics_item_df_.apply(lambda x: x["item_desc"].split(":")[1] if (club1 := x["item_desc"].split(":")[0]) in ["剧本杀"] else club1, axis=1)
    # club_two_desc = club_two_desc.to_frame().rename(columns={0: "desc"})
    # club_two_desc["desc"] = club_two_desc.apply(lambda x: x["desc"][:5] + "\n" + x["desc"][5:] if len(x["desc"]) > 5 else x["desc"], axis=1)
    # # ic(club_two_desc)
    # plotgenerator.count_plot(x="desc",
    #                          data=club_two_desc,
    #                          figwidth=80,
    #                          figheight=28,
    #                          new_xlabel="CLUB标签（剧本杀为二级标签，其他为一级标签）",
    #                          new_ylabel="动态的数量",
    #                          new_title="用户点赞动态在CLUB标签的数量分布",
    #                          new_fig_name=os.path.join(configs.visualization_folder_path, f"num_of_like_items_per_club2_dist.png"),
    #                          savefig=True
    #                          )

    # 每个用户点赞物品的数量分布，histplot
    like_df = like_df[["subject_id", "behavior"]]
    num_like_df = like_df.groupby(["subject_id"]).count().sort_values(by="behavior", ascending=False).reset_index()
    # print(like_df.head())
    num_like_df_log = np.log(num_like_df[["behavior"]])
    plotgenerator.hist_plot(x=num_like_df["behavior"],
                            figwidth=6,
                            figheight=4,
                            binwidth=10,
                            new_xlabel="用户点赞次数",
                            new_ylabel="用户相同点赞次数出现的数量",
                            new_title="用户点赞次数直方图",
                            new_fig_name=os.path.join(configs.visualization_folder_path, f"num_of_likes_per_user_dist.png"),
                            savefig=True
                            )


    # 点赞物品在所有club二级标签的数量分布

    # 每个物品被点赞的用户数量分布
    # 每个用户创建的剧本数量分布
    # 每个用户加入的club分布
    # 每个club中的用户加入数量分布


if __name__ == "__main__":
    cleaned_data_vis("data_20220222.xlsx")
