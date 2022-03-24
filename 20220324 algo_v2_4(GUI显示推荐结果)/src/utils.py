# encoding:utf-8
import os
import shutil

import configs


def create_folder_paths():
    """
    创建图片结果的文件夹路径
    :return:
    """
    if os.path.exists(configs.algo_result_folder_path):
        shutil.rmtree(configs.algo_result_folder_path)

    if os.path.exists(configs.qt_vid_folder_path):
        shutil.rmtree(configs.qt_vid_folder_path)
    os.mkdir(configs.algo_result_folder_path)
    os.mkdir(configs.rec_result_folder_path)
    os.mkdir(configs.perf_result_folder_path)
    os.mkdir(configs.like_img_folder_path)
    os.mkdir(configs.view_img_folder_path)
    os.mkdir(configs.gama_img_folder_path)
    os.mkdir(configs.qt_vid_folder_path)

