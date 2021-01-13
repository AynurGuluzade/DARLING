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
fig, (ax, ax2) = plt.subplots(1, 2) # create subplots

# mean rank bar chart
mr_treatment = [68.89, 66.46, 67.82, 66.01, 67.35, 65.18, 64.65]
mr_medicine = [25.67, 23.84, 25.57, 23.92, 24.97, 23.29, 22.86]
sub1_rects1 = ax.bar(x - width/2, mr_treatment, width, color='#CCE5FF', label='Treatment')
sub1_rects2 = ax.bar(x + width/2, mr_medicine, width, color='#FFCCE6', label='Medicine')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Mean Rank', labelpad=1)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=8, rotation=-45)
autolabel(ax, sub1_rects1)
autolabel(ax, sub1_rects2)

# hits@10 bar chart
hits10_treatment = [47.62, 50.48, 48.52, 50.97, 48.92, 51.32, 52.19]
hits10_medicine = [56.94, 59.71, 57.64, 60.25, 58.27, 60.97, 61.73]
sub2_rects1 = ax2.bar(x - width/2, hits10_treatment, width, color='#CCE5FF', label='_nolegend_')
sub2_rects2 = ax2.bar(x + width/2, hits10_medicine, width, color='#FFCCE6', label='_nolegend_')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax2.set_ylabel('Hits@10(%)', labelpad=0)
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontsize=8, rotation=-45)
autolabel(ax2, sub2_rects1)
autolabel(ax2, sub2_rects2)


fig.tight_layout()
plt.figlegend(loc='upper center', fancybox=True, shadow=True, ncol=2)
plt.show()
