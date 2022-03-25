# encoding:utf-8
"""
    该package用于实现算法2的步骤，算法过程包括：
    1.构建用户-物品点赞矩阵
    2.物品相似度矩阵计算
    3.预测用户对物品的点赞概率
    4.给点赞用户做推荐
"""
from .algo import run_item_cf, get_top_n