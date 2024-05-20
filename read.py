#Importing libraries 
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
import pprint
from scipy import stats
#matplotlib.matplotlib_fname()

"""
    GPU_TIME    WALL_TIME
METRIC 0.09         0.09
EVAL
BASH

"""

MEAN_COLUMN_INDEX = -2

dataframe = pd.read_csv("csv/results_final.csv")
dataframe = dataframe.set_index("event_id")
print(dataframe.loc["mean"])
