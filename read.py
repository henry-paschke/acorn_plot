#Importing libraries 
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
import pprint
from scipy import stats
#matplotlib.matplotlib_fname()

# Convert a given csv file into an excel file with columns "WALL_TIME and GPU_TIME"
def csv_to_excel(input_name, output_name):
    convert_frame(input_name).to_excel(output_name)

def plot_csv(input_name):
    figure, axes = plt.subplots(1, 1)
    axes.plot()
    plt.show()

# Print a given dataframe from the csv file
def print_from_csv(input_name):
    print(convert_frame(input_name))

# Return a new dataframe with columns "WALL_TIME and GPU_TIME"
def convert_frame(input_name):
    dataframe = pd.read_csv(input_name)
    dataframe = dataframe.set_index("event_id")

    # Fetch the mean values row
    mean_series = dataframe.loc["mean"]
    std_series = dataframe.loc["std"]

    labels = ["Metric_Learning", "Build_Graph", "Filtering", "Preprocess", "InteractionGNN", "ccInfer"]
    wall_time = []
    gpu_time = []

    for name, value in mean_series.items():
        if name.endswith("gpu_time"):
            gpu_time.append(f"{str(round(value, 4))} \u00B1 {str(round(std_series[name],4))}")
        elif name.endswith("time"):
            wall_time.append(f"{str(round(value, 4))} \u00B1 {str(round(std_series[name],4))}")

    # Construct the new dataframe
    data = {'':labels, "Wall_Time": wall_time, "GPU_Time": gpu_time}
    return pd.DataFrame(data)

#csv_to_excel("csv/results_final.csv", "excel/results_final.xlsx")
plot_csv("csv/results_final.csv")
