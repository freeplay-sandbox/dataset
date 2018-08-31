import matplotlib
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import seaborn
seaborn.set()

import time

fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, sharey=True)


df_annotations = pd.read_csv("annotations.csv")

plots = []

indices = {}
indices["task_engagement"] = ['goaloriented', 'aimless', 'adultseeking', 'noplay']
indices["social_engagement"] = ['solitary', 'onlooker', 'parallel', 'associative', 'cooperative']
indices["social_attitude"] = ['prosocial', 'adversarial', 'frustrated', 'assertive', 'passive']

for cls, ax in zip(["task_engagement", "social_engagement", "social_attitude"], (ax1, ax2, ax3)):
    df_cls = df_annotations[df_annotations["construct_class"] == cls]
    df_sum=df_cls.groupby(["age"])["duration"].sum()
    df_sum_construct=df_cls.groupby(["construct", "age"])["duration"].sum()
    df=df_sum_construct/df_sum
    df.unstack().plot.bar(ax=ax, width=0.8)


##plt.title('Title 2', fontsize=16)
#plt.xlabel('Annotated construct class', fontsize=14)
##plt.legend(['Child-child', 'Child-robot'])
#

#handle, legend = 


formatter = matplotlib.ticker.FuncFormatter(lambda s, x: "%d%%" % int(s * 100))

xformatter = matplotlib.ticker.FuncFormatter(lambda s, x: "child-robot" if "robot" in s else "child-child")

for cls, ax in zip(["task_engagement", "social_engagement", "social_attitude"], (ax1, ax2, ax3)):
    ax.set_ylabel("Construct distribution per age", fontsize=20)
    #ax.set_yticks(np.arange(0, 1*60, 30*60))
    #ax.set_yticklabels(np.arange(0, 1*60, 30*60))

    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.grid()
    ax.set_axisbelow(True) # plot grid line below bar plots
    #ax.xaxis.set_major_formatter(xformatter)
    ax.set_xlabel("")
    for i in ax.get_xticklabels(): i.set_rotation(30)
    ax.get_legend().set_title("Age")
    ax.set_title(cls.replace("_", " "), fontsize=20)

    #handles, labels = ax.get_legend_handles_labels()
    #handles = [dict(zip(labels, handles))[construct] for construct in indices[cls]]
    #labels = indices[cls]
    #ax.legend(handles, labels)


plt.show()
