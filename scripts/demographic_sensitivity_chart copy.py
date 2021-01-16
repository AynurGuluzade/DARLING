import matplotlib
import matplotlib.pyplot as plt
import numpy as np

def autolabel(ax, rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, 0.85 * height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=6,
                    rotation=90)

labels = ['Gender', 'Age', 'Ethnic', 'G+A', 'G+E', 'A+E', 'All']

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars
fig, (ax, ax1) = plt.subplots(2, 2) # create subplots

# mean rank chart with probabilities
ax[0].set_ylabel('Mean Rank', labelpad=1)
mr_treatment_prob = ax[0].bar(x - width/2, [68.89, 66.46, 67.82, 66.01, 67.35, 65.18, 64.65], width, color='#CCE5FF', label='Treatment')
mr_medicine_prob = ax[0].bar(x + width/2, [25.67, 23.84, 25.57, 23.92, 24.97, 23.29, 22.86], width, color='#FFCCE6', label='Medicine')
ax[0].set_xticks(x)
ax[0].set_xticklabels(labels, fontsize=8, rotation=-15)
autolabel(ax[0], mr_treatment_prob)
autolabel(ax[0], mr_medicine_prob)

# mean rank chart without probabilities
mr_treatment_without = ax[1].bar(x - width/2, [71.11, 69.32, 69.28, 68.83, 70.14, 67.83, 67.18], width, color='#CCE5FF', label='_nolegend_')
mr_medicine_without = ax[1].bar(x + width/2, [27.13, 25.16, 26.86, 24.97, 26.46, 25.01, 24.89], width, color='#FFCCE6', label='_nolegend_')
ax[1].set_xticks(x)
ax[1].set_xticklabels(labels, fontsize=8, rotation=-15)
autolabel(ax[1], mr_treatment_without)
autolabel(ax[1], mr_medicine_without)

# hits@10 bar chart
ax1[0].set_ylabel('Hits@10(%)', labelpad=0)
ax1[0].set_xlabel('With Probability Score', labelpad=0)
hits10_treatment_prob = ax1[0].bar(x - width/2, [47.62, 50.48, 48.52, 50.97, 48.92, 51.32, 52.19], width, color='#CCE5FF', label='_nolegend_')
hits10_medicine_prob = ax1[0].bar(x + width/2, [56.94, 59.71, 57.64, 60.25, 58.27, 60.97, 61.73], width, color='#FFCCE6', label='_nolegend_')
ax1[0].set_xticks(x)
ax1[0].set_xticklabels(labels, fontsize=8, rotation=-15)
autolabel(ax1[0], hits10_treatment_prob)
autolabel(ax1[0], hits10_medicine_prob)

# hits@10 bar chart
ax1[1].set_xlabel('Without Probability Score', labelpad=0)
hits10_treatment_without = ax1[1].bar(x - width/2, [45.83, 48.17, 46.85, 48.17, 45.96, 48.25, 50.41], width, color='#CCE5FF', label='_nolegend_')
hits10_medicine_without = ax1[1].bar(x + width/2, [54.58, 57.94, 55.42, 58.09, 56.12, 59.31, 59.96], width, color='#FFCCE6', label='_nolegend_')
ax1[1].set_xticks(x)
ax1[1].set_xticklabels(labels, fontsize=8, rotation=-15)
autolabel(ax1[1], hits10_treatment_without)
autolabel(ax1[1], hits10_medicine_without)


fig.tight_layout()
plt.figlegend(loc='upper center', fancybox=True, shadow=True, ncol=2)
plt.show()
