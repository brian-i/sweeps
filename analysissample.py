'''
Sample analysis run for a series of generated data
Uses sweeps package and sweeps_analysis.py

Version 2!

Created: November 2019
'''

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
HEAT_DF = pd.DataFrame()
for index, row in DF.iterrows():
    HEAT_DF = HEAT_DF.combine_first(pd.DataFrame(
        [row.success], index=[row.F_j], columns=[row.F_h]))
print('\n\nHeatmap DataFrame:')
print(HEAT_DF)

# Create heatmap plot:
CANV, AX = plt.subplots(figsize=(8, 6))
FIG = sns.heatmap(
    HEAT_DF.iloc[::-1], cmap="hot", annot=True, fmt='.2f',
    xticklabels=HEAT_DF.iloc[::-1].columns.values.round(2),
    yticklabels=HEAT_DF.iloc[::-1].index.values.round(2))
plt.show()
