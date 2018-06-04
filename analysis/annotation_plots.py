import matplotlib
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

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
    df_reshaped = df_cls.groupby(["condition", "construct"])["duration"].sum().unstack().fillna(0)
    #df_reshaped.plot(ax=ax, kind="bar", stacked=True)
    #df_reshaped.set_index("construct")
    plots.append(df_reshaped.T.reindex(index=reversed(indices[cls])).T.plot(ax=ax, kind="bar", stacked=True, legend='reverse'))

##plt.title('Title 2', fontsize=16)
#plt.xlabel('Annotated construct class', fontsize=14)
plt.yticks(np.arange(0, 50*3600, 3600*5))
#plt.ylabel('Duration', fontsize=14)
##plt.legend(['Child-child', 'Child-robot'])
#

#handle, legend = 


formatter = matplotlib.ticker.FuncFormatter(lambda s, x: "%02dh%02dm" % (s // 3600, (s % 3600) // 60))

xformatter = matplotlib.ticker.FuncFormatter(lambda s, x: "child-robot" if "robot" in s else "child-child")

for cls, ax in zip(["task_engagement", "social_engagement", "social_attitude"], (ax1, ax2, ax3)):
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.grid()
    ax.set_axisbelow(True) # plot grid line below bar plots
    #ax.xaxis.set_major_formatter(xformatter)
    ax.set_xlabel("")
    for i in ax.get_xticklabels(): i.set_rotation(0)
    ax.get_legend().set_title("")
    ax.set_title(cls.replace("_", " "), fontsize=20)

    #handles, labels = ax.get_legend_handles_labels()
    #handles = [dict(zip(labels, handles))[construct] for construct in indices[cls]]
    #labels = indices[cls]
    #ax.legend(handles, labels)


plt.show()
