# encoding:utf-8
import os

import numpy as np
import pandas as pd
from icecream import ic
import sys
sys.dont_write_bytecode = True

import configs
import plotting


def itemCF_tuning_vis():
    my_plot = plotting.PlotGenerator()
    f_scores = np.load(os.path.join(configs.perf_result_folder_path, "item_cf_tuning.npy"))
    sim_thres_range = np.arange(0.5, 0.8, 0.03)
    pred_thres_range = np.arange(0, 0.2, 0.04)
    df = pd.DataFrame({
        "sim_thres": np.tile(sim_thres_range, pred_thres_range.size),
        "f_score": f_scores.flatten("F"),
        "pred_thres": np.repeat(pred_thres_range, sim_thres_range.size)
    })
    my_plot.line_plot(x="sim_thres",
                      y="f_score",
                      hue="pred_thres",
                      data=df,
                      figwidth=24,
                      figheight=20,
                      ylim_low=0.0255,
                      ylim_high=0.0295,
                      legend_fontsize=30,
                      xtick_fontsize=40,
                      ytick_fontsize=40,
                      xtick_rot=0,
                      xlabel_fontsize=50,
                      ylabel_fontsize=50,
                      title_fontsize=60,
                      new_legend_labels=[f'prediction threshold={"%.2f" % i}' for i in pred_thres_range],
                      new_xlabel="similarity threshold",
                      new_ylabel="f1-score",
                      new_title=f"Item-based CF模型的调参结果",
                      new_fig_name=os.path.join(configs.perf_result_folder_path, f"item_cf_tuning.png"),
                      savefig=True
                      )

def userCF_tuning_vis():
    my_plot = plotting.PlotGenerator()
    f_scores = np.load(os.path.join(configs.perf_result_folder_path, "user_cf_tuning.npy"))
    sim_thres_range = np.arange(0.2, 0.4, 0.02)
    pred_thres_range = np.arange(0.12, 0.24, 0.02)
    df = pd.DataFrame({
        "sim_thres": np.tile(sim_thres_range, pred_thres_range.size),
        "f_score": f_scores.flatten("F"),
        "pred_thres": np.repeat(pred_thres_range, sim_thres_range.size)
    })
    my_plot.line_plot(x="sim_thres",
                      y="f_score",
                      hue="pred_thres",
                      data=df,
                      figwidth=24,
                      figheight=20,
                      ylim_low=0.0286,
                      ylim_high=0.02883,
                      legend_fontsize=30,
                      xtick_fontsize=40,
                      ytick_fontsize=40,
                      xtick_rot=0,
                      xlabel_fontsize=50,
                      ylabel_fontsize=50,
                      title_fontsize=60,
                      new_legend_labels=[f'prediction threshold={"%.2f" % i}' for i in pred_thres_range],
                      new_xlabel="similarity threshold",
                      new_ylabel="f1-score",
                      new_title=f"User-based CF模型的调参结果",
                      new_fig_name=os.path.join(configs.perf_result_folder_path, f"user_cf_tuning.png"),
                      savefig=True
                      )


if __name__ == "__main__":
    itemCF_tuning_vis()
    userCF_tuning_vis()
    user_cf_params = np.load(os.path.join(configs.perf_result_folder_path, "user_cf_params.npy"))
    item_cf_params = np.load(os.path.join(configs.perf_result_folder_path, "item_cf_params.npy"))
    ic(user_cf_params)
    ic(item_cf_params)
