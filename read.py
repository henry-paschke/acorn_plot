#Importing libraries 
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
import pprint
from scipy import stats
#matplotlib.matplotlib_fname()

dataframe = pd.read_csv("csv/results_final.csv")
print(dataframe)