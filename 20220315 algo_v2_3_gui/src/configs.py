# encoding:utf-8
import os.path


root_folder_path = os.path.abspath(os.path.join(__file__, ".."))
root_folder_path = os.path.abspath(os.path.join(root_folder_path, ".."))
# print(root_folder_path)

src_folder_path = os.path.join(root_folder_path, "src")
data_folder_path = os.path.join(root_folder_path, "data")
qt_img_folder_path = os.path.join(root_folder_path, "img")
visualization_folder_path = os.path.join(root_folder_path, "visualization_results")
algo_result_folder_path = os.path.join(root_folder_path, "algo_results")

rec_result_folder_path = os.path.join(algo_result_folder_path, "rec_result")
perf_result_folder_path = os.path.join(algo_result_folder_path, "perf_result")

view_img_folder_path = os.path.join(algo_result_folder_path, "view")
like_img_folder_path = os.path.join(algo_result_folder_path, "like")
gama_img_folder_path = os.path.join(algo_result_folder_path, "gama")


__all__ = ["src_folder_path", "data_folder_path", "qt_img_folder_path", "visualization_folder_path", "algo_result_folder_path",
           "perf_result_folder_path", "rec_result_folder_path", "view_img_folder_path",
           "like_img_folder_path", "gama_img_folder_path"]
# 当使用from config import * 时，只能export这些路径
