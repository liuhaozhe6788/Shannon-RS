# encoding:utf-8
"""
    该package用于对所有用户或者单个用户运行选中的算法
"""
from .run import run_all_users, run_all_algos
from .generalized_cf import GeneralizedCF
from .item_cf import get_top_n, run_item_cf
