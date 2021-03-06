import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pyplotz.pyplotz import PyplotZ
import sys
sys.dont_write_bytecode = True

import configs


class PlotGenerator:

    def __init__(self, style="whitegrid", rotation=0, palette="dark"):
        self._style = style
        self._rotation = rotation
        self._palette = palette

    @staticmethod
    def show_values(axs, orient="v", space=.01):
        def _single(ax):
            if orient == "v":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() / 2
                    _y = p.get_y() + p.get_height() + (p.get_height() * 0.01)
                    value = '{:.3f}'.format(p.get_height()) if p.get_height() != 0 else "0"
                    ax.text(_x, _y, value, ha="center", size="medium")
            elif orient == "h":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() + float(space)
                    _y = p.get_y() + p.get_height() - (p.get_height() * 0.5)
                    value = '{:.3f}'.format(p.get_width())
                    ax.text(_x, _y, value, ha="left", size="medium")

        if isinstance(axs, np.ndarray):
            for idx, ax in np.ndenumerate(axs):
                _single(ax)
        else:
            _single(axs)

    def count_plot(self, x, data, figwidth, figheight, new_xlabel, new_ylabel, new_title, new_fig_name=None, savefig=False, show_bar_value=False):
        pltz = PyplotZ()
        pltz.enable_chinese()
        sns.set_style(self._style)
        plt.figure(figsize=(figwidth,figheight))
        ax = sns.countplot(x=x, data=data, palette=self._palette)
        if show_bar_value:
            self.show_values(ax)
        pltz.xticks(rotation=0, fontsize=40)
        pltz.yticks(fontsize=40)
        pltz.xlabel(new_xlabel, fontsize=45)
        pltz.ylabel(new_ylabel, fontsize=45)
        pltz.title(new_title, fontsize=60)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)

    def scatter_plot(self, data, new_xlabel, new_ylabel, new_title, x=None, y=None, isgrouped=False, hue=None, new_legend_labels=None, new_legend_title=None,
                     new_fig_name=None, savefig=False, show_point_value=False):
        sns.set_style(self._style)
        pltz = PyplotZ()
        pltz.enable_chinese()
        ax = sns.scatterplot(data=data, x=x, y=y, hue=hue, palette=self._palette)
        if isgrouped:
            legend_labels_obj, legend_labels = ax.get_legend_handles_labels()
            ax.legend(legend_labels_obj, new_legend_labels, title=new_legend_title)
        if show_point_value:
            self.show_values(ax)
        plt.xticks(rotation=self._rotation, fontsize=5)
        pltz.xlabel(new_xlabel)
        pltz.ylabel(new_ylabel)
        pltz.title(new_title)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)

    def hist_plot(self, x, new_xlabel, new_ylabel, new_title, figwidth, figheight, y=None, binwidth=None, isgrouped=False, hue=None, new_legend_labels=None, new_legend_title=None,
                  new_fig_name=None, savefig=False, show_point_value=False):
        sns.set_style(self._style)
        pltz = PyplotZ()
        pltz.enable_chinese()
        plt.figure(figsize=(figwidth, figheight))
        ax = sns.histplot(x=x, y=y, hue=hue, binwidth=binwidth, palette=self._palette)
        if isgrouped:
            legend_labels_obj, legend_labels = ax.get_legend_handles_labels()
            ax.legend(legend_labels_obj, new_legend_labels, title=new_legend_title)
        if show_point_value:
            self.show_values(ax)
        plt.xticks(rotation=0)
        pltz.xlabel(new_xlabel)
        pltz.ylabel(new_ylabel)
        pltz.title(new_title)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)
        # plt.show()

    def box_plot(self, new_xlabel, new_title, x=None, y=None, isgrouped=False, hue=None, new_legend_labels=None, new_legend_title=None,
                 new_fig_name=None, savefig=False, show_point_value=False):
        sns.set_style(self._style)
        pltz = PyplotZ()
        pltz.enable_chinese()
        ax = sns.boxplot(x=x, y=y, hue=hue, palette=self._palette)
        if isgrouped:
            legend_labels_obj, legend_labels = ax.get_legend_handles_labels()
            ax.legend(legend_labels_obj, new_legend_labels, title=new_legend_title)
        if show_point_value:
            self.show_values(ax)
        plt.xticks(rotation=self._rotation)
        pltz.xlabel(new_xlabel)
        pltz.title(new_title)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)

    def line_plot(self, clubs, data, figwidth, figheight, new_xlabel=None, new_ylabel=None, new_title=None, new_legend_labels=None,
                  new_fig_name=None, savefig=False, show_point_value=True):
        pltz = PyplotZ()
        pltz.enable_chinese()
        plt.figure(figsize=(figwidth, figheight))
        sns.set_style(self._style)
        ax = sns.lineplot(data=data, palette=self._palette)
        if show_point_value:
            self.show_values(ax)
        pltz.legend(labels=new_legend_labels, fontsize=10)
        pltz.xticks(range(len(clubs)), clubs, rotation=self._rotation, fontsize=10)
        pltz.yticks(fontsize=10)
        pltz.xlabel(new_xlabel, fontsize=10)
        pltz.ylabel(new_ylabel, fontsize=10)
        pltz.title(new_title, fontsize=15)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)

    def bar_plot(self, figwidth, figheight, x, y, hue, data, new_xticks, new_legend_labels, new_xlabel,
                  new_ylabel, new_title, new_fig_name=None, savefig=False, show_point_value=True):
        pltz = PyplotZ()
        pltz.enable_chinese()
        plt.figure(figsize=(figwidth, figheight))
        sns.set_style(self._style)
        ax = sns.barplot(x=x, y=y,  hue=hue, data=data, palette=self._palette)
        if show_point_value:
            self.show_values(ax)
        pltz.legend(labels=new_legend_labels)
        plt.setp(ax.get_legend().get_texts(), fontsize='15')
        pltz.xticks(range(len(new_xticks)), new_xticks, rotation=self._rotation, fontsize=20)
        pltz.yticks(fontsize=20)
        pltz.xlabel(new_xlabel, fontsize=20)
        pltz.ylabel(new_ylabel, fontsize=20)
        pltz.title(new_title, fontsize=30)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)

    def bar_plots(self, figwidth, figheight, x, y, hue, data, new_xticks, new_legend_labels, new_xlabel=None,
                  new_ylabel=None, new_titles=None, new_fig_name=None, savefig=False, show_point_value=True):
        pltz = PyplotZ()
        pltz.enable_chinese()
        plt.figure(figsize=(figwidth, figheight))
        sns.set_style(self._style)
        for i in range(len(data)):
            plt.subplot(len(data), 1, i+1)
            ax = sns.barplot(x=x, y=y,  hue=hue, data=data[i], palette=self._palette)
            if show_point_value:
                self.show_values(ax)
            pltz.legend(labels=new_legend_labels)
            plt.setp(ax.get_legend().get_texts(), fontsize='20')
            pltz.xticks(range(len(new_xticks)), new_xticks, rotation=self._rotation, fontsize=20)
            pltz.yticks(fontsize=30)
            pltz.xlabel(new_xlabel, fontsize=30)
            pltz.ylabel(new_ylabel, fontsize=30)
            pltz.title(new_titles[i], fontsize=40)
        plt.subplots_adjust(hspace=1)
        if savefig:
            plt.savefig(new_fig_name, dpi=100)


if __name__ == "__main__":
    print(pd.Series(data=[1, 2]))
    my_plot = PlotGenerator()
    # my_plot.bar_plots(data=[pd.DataFrame({"x_value": [1, 2, 1, 2],"y_value": [1, 2, 3, 4], "cat": [1, 1, 2, 2]}),
    #                         pd.DataFrame({"x_value": [1, 2, 1, 2],"y_value": [1, 2, 3, 4], "cat": [1, 1, 2, 2]}),
    #                         ],
    #                   x="x_value",
    #                   y="y_value",
    #                   hue="cat",
    #                   figwidth=20,
    #                   figheight=20,
    #                   new_xticks=["a", "b"],
    #                   new_legend_labels=[f'????????????????????????club????????????????????????', f'???????????????club????????????????????????'],
    #                   new_xlabel="club??????",
    #                   new_ylabel="???????????????",
    #                   new_titles=[1, 2],
    #                   new_fig_name=os.path.join(configs.perf_result_folder_path, f"pseudo_result.png"),
    #                   savefig=True
    #                   )

