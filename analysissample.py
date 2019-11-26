'''
Sample analysis run for a series of generated data
Uses sweeps package and sweeps_analysis.py

Created: November 2019
'''

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1,
                '/Users/brian/Documents/Cornell/Quantum Research 2019/'
                'GitHub.nosync/sweeps/')
import sweeps_analysis
sns.set()

LOCATION = os.getcwd()
DF = sweeps_analysis.get_DataFrame(LOCATION)

# Sort values:
DF.sort_values(["F_h", "F_j"], axis=0,
               ascending=True, inplace=True)

# Add success probability to DataFrame:
SUCCESS_LIST = []
for index, row in DF.iterrows():
    SUCCESS_LIST.append(float(sweeps_analysis.get_data(index, LOCATION)))
DF['success'] = pd.Series(SUCCESS_LIST, index=DF.index)
print('\n\nSorted, with success probabilities:')
print(DF)

# Create a new DataFrame representing the F_j vs. F_h heatmap:
HEAT_FRAMES = []
for index, row in DF.iterrows():
    # print(pd.DataFrame([row.success], index=[row.F_j], columns=[row.F_h]))
    # print('-')
    HEAT_FRAMES.append(
        pd.DataFrame([row.success], index=[row.F_j], columns=[row.F_h]))
HEAT_DF = pd.concat(HEAT_FRAMES)
print(HEAT_DF)

NUNIQUE_F_H = DF.nunique()[0]
NUNIQUE_F_J = DF.nunique()[1]
MIN_F_H = DF['F_h'].iloc[0]
MIN_F_J = DF['F_j'].iloc[0]
MAX_F_H = DF['F_h'].iloc[-1]
MAX_F_J = DF['F_j'].iloc[-1]
# print(((DF.diff()[DF.diff() > 0].loc[:, ['F_h', 'F_j']].min()[0])))
MAP = np.zeros((int(np.ceil(MAX_F_H /
                            DF.diff()[DF.diff() > 0].loc[
                                :, ['F_h', 'F_j']].min()[0])),
                int(np.ceil(MAX_F_J /
                            DF.diff()[DF.diff() > 0].loc[
                                :, ['F_h', 'F_j']].min()[1]))))
for index, row in DF.iterrows():
    # print(min(int((
    #   row.F_h - MIN_F_H) / MAX_F_H * NUNIQUE_F_H), NUNIQUE_F_H - 1))
    # print(min(int((row.F_j - MIN_F_J) / MAX_F_J * NUNIQUE_F_J),
    #           NUNIQUE_F_J - 1))
    # print('-')
    MAP[min(int((row.F_h - MIN_F_H) / MAX_F_H * NUNIQUE_F_H), NUNIQUE_F_H - 1),
        min(int((row.F_j - MIN_F_J) / MAX_F_J * NUNIQUE_F_J),
            NUNIQUE_F_J - 1)] = (float(sweeps_analysis.get_data(index,
                                                                LOCATION)))

AX = sns.heatmap(
    MAP[::-1], cmap='hot', square=True,
    xticklabels=np.linspace(MIN_F_H, MAX_F_H, NUNIQUE_F_H).round(2),
    yticklabels=np.linspace(MAX_F_J, MIN_F_J, NUNIQUE_F_J).round(2))

AX.figure.tight_layout()
# plt.pcolormesh(MAP, cmap='hot')
plt.show()
