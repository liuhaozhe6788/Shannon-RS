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
from .item_cf import ItemCF
np.set_printoptions(threshold=np.inf)


class UserCF(ItemCF):

    def __init__(self, database, buffer_name, sim_thres=0, pred_thres=1,train_data=None, test_flag=False, filter_flag=True):

        super().__init__(database, buffer_name, sim_thres, pred_thres, train_data, test_flag, filter_flag)

    def calc_user_similarities(self, ui_matrix: np.ndarray) -> np.ndarray:
        user_similarities_ = pairwise_distances(ui_matrix, metric="cosine")
        user_similarities_ = np.ones(user_similarities_.shape) - user_similarities_
        user_similarities_filtered_ = self.compare_and_filter(user_similarities_)

        return user_similarities_filtered_

    @staticmethod
    def predict(ui_matrix: np.ndarray, user_similarities_: np.ndarray) -> np.ndarray:
        mean_user_rating = ui_matrix.mean(axis=1)
        ratings_diff = ui_matrix - mean_user_rating[:, np.newaxis]
        pred = mean_user_rating[:, np.newaxis] + user_similarities_.dot(ratings_diff)/ (np.array([np.abs(user_similarities_).sum(axis=1)]).T)
        return pred

    def get_pred(self):
        ui_matrix = self.create_ui_matrix()
        user_similarities_ = self.calc_user_similarities(ui_matrix)
        pred = self.predict(ui_matrix, user_similarities_)
        return pred
