# encoding:utf-8
import os
import re
import PIL
import requests
import io
import numpy as np
import pandas as pd
from icecream import ic

import configs
from database import check


def clean_data(raw_file):
    """
    数据清洗，去掉含缺失值的记录和转换数据格式
    :param raw_file: 源文档
    :return:
    """
    item_df = pd.read_excel(raw_file, sheet_name="item_data")
    user_df = pd.read_excel(raw_file, sheet_name="user_data")
    # print(f"物品数据前5行：\n{item_df.head()}")
    # print(f"用户数据前5行：\n{user_df.head()}")

    ####删除动态描述为空的动态物品记录####
    # print(item_df.loc[0, 'item_desc'] == np.nan)
    # print(item_df[item_df["item_desc"].isna()])
    dymamics_cnt = len(item_df[item_df["content_type"] == "动态"])
    dymamics_dropped_cnt = len(item_df[(item_df["content_type"] == "动态") & (item_df["item_desc"].isna())])
    # print(f"所有动态的个数：{dymamics_cnt}")
    # print(f"删去动态的个数：{dymamics_dropped_cnt}")
    desc_missing_ratio = len(item_df[(item_df["content_type"] == "动态") & (item_df["item_desc"].isna())])/len(item_df[item_df["content_type"] == "动态"])
    # print(f"动态描述缺失率为：{desc_missing_ratio*100}%\n")

    items_dropped = item_df[(item_df["content_type"] == "动态") & (item_df["item_desc"].isna())]
    items_dropped = list(items_dropped["item_id"])

    ####删除动态:7546，动态描述的二级标签有误####
    items_dropped += ["动态:7546"]
    item_df = item_df[~(item_df["item_id"].isin(items_dropped))]

    ####更改缺失值为“*”####
    def set_nan(author_id):
        if author_id == 0:
            return None
        else:
            return author_id
    item_df["author_id"] = item_df.apply(lambda x: set_nan(x["author_id"]), axis=1)
    item_df = item_df.fillna("*")

    ####删除物品对应的用户行为记录####
    # print(items_dropped)
    likes_cnt = len(user_df[user_df["behavior"] == "like"])
    items_dropped += list(user_df[(user_df["behavior"] == "like") & ~(user_df["object_id"].isin(list(item_df["item_id"])))]["object_id"])

    # likes_dropped_cnt = len(user_df[(user_df["behavior"] == "like") & user_df["object_id"].isin(items_dropped)])
    # # print(f"所有点赞行为的个数：{likes_cnt}")
    # # print(f"删去点赞的个数：{likes_dropped_cnt}")
    # likes_dropped_ratio = likes_dropped_cnt/likes_cnt
    # # print(f"点赞缺失率为：{likes_dropped_ratio * 100}%\n")
    user_df = user_df[~(user_df["subject_id"].isin(items_dropped) | user_df["object_id"].isin(items_dropped))]
    user_df = user_df.fillna("*")

    ####删除点赞次数小于0的用户的行为记录####
    like_df = user_df[user_df["behavior"] == "like"].copy()
    like_df = like_df[["subject_id", "behavior"]]
    num_like_df = like_df.groupby(["subject_id"]).count().sort_values(by="behavior", ascending=False).reset_index()
    num_like_df = num_like_df[num_like_df["behavior"] <= 0]
    users_dropped = list(num_like_df["subject_id"])
    user_df = user_df[~(user_df["subject_id"].isin(users_dropped) | user_df["object_id"].isin(users_dropped))]

    ####更改时间和URL的格式####
    # print(item_df.loc[0, "publish_time"])

    item_df["publish_time"] = item_df.apply(lambda x: "-".join(str(x["publish_time"]).split("_")[:3]) +
                                                      " " +
                                                      ":".join(str(x["publish_time"]).split("_")[3:]),
                                            axis=1)
    user_df["time"] = user_df.apply(lambda x: "-".join(str(x["time"]).split("_")[:3]) +
                                              " " +
                                              ":".join(str(x["time"]).split("_")[3:]),
                                    axis=1)
    # print(item_df["publish_time"])
    item_df["image_url"] = item_df.apply(lambda x: str(x["image_url"]).replace("_https_", ",https:").replace("https_", "https:"),
                                         axis=1)
    item_df["video_url"] = item_df.apply(lambda x: str(x["video_url"]).replace("_https_", ",https:").replace("https_", "https:"),
                                         axis=1)

    ####修改动态的item_desc,将第一级标签剧本杀修改为第二级标签####
    dynamics_df = item_df[item_df["content_type"] == "动态"].copy()
    dynamics_df["item_desc"] = dynamics_df.apply(lambda x: x["item_desc"].split(":")[1] if (club1 := x["item_desc"].split(":")[0]) in ["剧本杀"] else club1,
                                                 axis=1)

    ####删除部分剧本杀动态
    # user_df_copy = user_df.copy()
    # user_df_copy = user_df_copy.rename({"object_id": "item_id"}, axis=1)
    # user_df_copy = pd.merge(user_df_copy, dynamics_df[["item_id", "item_desc"]], on="item_id")
    # user_df_copy = user_df_copy[user_df_copy["item_desc"] == "剧本杀"]
    # user_df_copy = user_df_copy.sample(frac=.2)
    # items_dropped = user_df_copy["item_id"]
    # user_df = user_df[~(user_df["subject_id"].isin(items_dropped) | user_df["object_id"].isin(items_dropped))]

    ####增加club_data####
    ####增加club精选####
    club_df = dynamics_df.groupby(["item_desc"]).apply(lambda x: ",".join(list(x["item_id"]))).reset_index()
    club_df.columns = ["club", "items"]
    # print(club_df)

    ####增加推广集####
    n_promo_items = 80
    liked_df = user_df[user_df["behavior"] == "like"].copy()
    liked_df = liked_df[["behavior", "object_id"]]
    liked_df = liked_df.groupby(["object_id"]).count().sort_values(by="behavior", ascending=False).reset_index()
    # print(liked_df)
    promo_items = list(liked_df["object_id"])[: min(n_promo_items, len(liked_df))]
    # print(f"推广集：{promo_items}，长度为{len(promo_items)}")
    club_df.loc[len(club_df)]=["推广集", ",".join(promo_items)]
    # print(club_df)

    with pd.ExcelWriter(os.path.join(configs.data_folder_path, "cleanedData.xlsx")) as writer:
        item_df.to_excel(writer, sheet_name='item_data', index=False)
        user_df.to_excel(writer, sheet_name='user_data', index=False)
        club_df.to_excel(writer, sheet_name='club_data', index=False)

    return user_df, item_df, club_df


def to_records(data_path):
    def process_single_data(v):
        if pd.isna(v):
            return None
        elif isinstance(v, float) and v == int(v):
            return int(v)
        elif isinstance(v, str):
            return v.strip()
        else:
            return v

    user_df, item_df, club_df = clean_data(data_path)
    # 读取user_data
    for idx, row in user_df.iterrows():
        if (behavior := process_single_data(row.get("behavior"))) is None:
            continue
        elif behavior == "join":
            for i in str(process_single_data(row.get("object_id"))).split(','):
                # print("user", process_single_data(row.get("subject_id")), behavior, "club", "动态:二级标签:" + (i.split(":")[2] if (club1 := i.split(":")[1]) in ["剧本杀"] else club1))
                yield ["user", process_single_data(row.get("subject_id")), behavior, "club", "动态:二级标签:" +
                       (i.split(":")[2] if (club1 := i.split(":")[1]) in ["剧本杀"] else club1)]
            continue
        elif behavior == "follow":
            obj_type = "user"
        elif behavior in ["view", "like", "create", "comment"]:
            obj_type = "item"
        else:
            continue
        for i in str(process_single_data(row.get("object_id"))).split(','):
            yield ["user", process_single_data(row.get("subject_id")), behavior, obj_type, i]

    # 读取item_data
    for idx, row in item_df.iterrows():
        item_id = process_single_data(row.get("item_id"))
        if item_desc := process_single_data(row.get("item_desc")):
            r = iter(str(item_desc).split(":"))

            if (item_type := item_id.split(':')[0]) == "剧本":
                for club_type in ["类型", "主题", "背景", "难度", "销售类型"]:
                    for v in next(r).split(","):
                        if v != "*":
                            yield ["item", item_id, "have", "club",
                                   "{}:{}:{}".format(item_type, club_type, v)]
                for label in ["剧本评分", "恐怖评分", "情感评分", "欢乐评分", "烧脑评分"]:
                    for v in next(r).split(","):
                        if v != "*":
                            yield ["item", item_id, "have", label, v]
            elif item_type == "动态":
                v = item_desc.split(":")
                for club_type in ["二级标签"]:
                    # print(["item", item_id, "have", "club", "{}:{}:{}".format(item_type, club_type, v[1] if (club1 := v[0]) in ["剧本杀"] else club1)])
                    yield ["item", item_id, "have", "club",
                           "{}:{}:{}".format(item_type, club_type, v[1] if (club1 := v[0]) in ["剧本杀"] else club1)]
            elif item_type == "文章":
                pass
            elif item_type == "游戏":
                for club_type in ["类型"]:
                    for v in next(r).split(","):
                        if v != "*":
                            yield ["item", item_id, "have", "club",
                                   "{}:{}:{}".format(item_type, club_type, v)]
            elif item_type == "评论":
                for label in ["source"]:
                    for v in next(r).split(","):
                        if v != "*":
                            yield ["item", item_id, "have", label, v]
            elif item_type == "店铺":
                for club_type in ["类型"]:
                    for v in next(r).split(","):
                        if v != "*":
                            yield ["item", item_id, "have", "club",
                                   "{}:{}:{}".format(item_type, club_type, v)]
            else:
                continue
        for i in ["author_id", "publish_time", "content_title", "content_text", "image_url", "video_url"]:
            if (v := process_single_data(row.get(i))) is not None:
                if isinstance(v, str) and check.behavior_info(("item", "have", i))["multiple"]:
                    for v in v.split(','):
                        if v != "*":
                            yield ["item", item_id, "have", i, v]
                else:
                    if v != "*":
                        yield ["item", item_id, "have", i, v]

    # 读取club_data
    for idx, row in club_df.iterrows():
        club = process_single_data(row["club"])
        if (v := process_single_data(row.get("items"))) is not None:
            for v in str(v).split(','):
                yield ["club", "动态:二级标签:" + club, "have", "selected_item", v]


if __name__ == "__main__":
    raw_data_path = os.path.join(configs.data_folder_path, "data_20220222.xlsx")

    for i in to_records(raw_data_path):
        pass
