import matplotlib.pyplot as plt

# fig, ax = plt.subplots()

tuplesForMachineAxis = [(0, 5.0), (5.0, 23.0), (56.0, 10.0), (66.0, 23.0)]
colorsForMachineAxis = [[0.939024538252132, 0.36507614685173545, 0.3565285916220526],
[0.9749627588378018, 0.9329646336549795, 0.8948111139503152],
[0.9749627588378018, 0.9329646336549795, 0.8948111139503152],
[0.6899567279447018, 0.3385853325423532, 0.976279173152431]]
# plt.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='tab:blue')
# plt.broken_barh(tuplesForMachineAxis, (20, 9),
#                facecolors = colorsForMachineAxis)
plt.broken_barh(tuplesForMachineAxis, (10, 9), facecolors=colorsForMachineAxis)
# plt.ylim(5, 35)
# plt.xlim(0, 200)
# plt.xlabel('seconds since start')
# plt.yticks([15, 25], labels=['Bill', 'Jim'])
plt.grid(True)
# plt.annotate('race interrupted', (61, 25),
#             xytext=(0.8, 0.9), textcoords='axes fraction',
#             arrowprops=dict(facecolor='black', shrink=0.05),
#             fontsize=16,
#             horizontalalignment='right', verticalalignment='top')

plt.show()