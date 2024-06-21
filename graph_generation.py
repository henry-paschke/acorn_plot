#Importing libraries 
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
import numpy as np


# Convert a given csv file into an excel file with columns "WALL_TIME and GPU_TIME"
def csv_to_excel(input_name: str, output_name: str) -> None:
    convert_frame(input_name).to_excel(output_name)

def quad_func(x, a, b, c):
    return a * x**2 + b * x + c

# Plot a given csv file to an output file
def plot_points(input_name: str, output_name: str, x: str, y: str, x_label: str = "", y_label: str = "", x_bounds: list = None, y_bounds: list = None, curve_type ="q") -> None:

    # Rows to drop from the dataframe
    drop_labels = ["mean", "std"]

    #Fetch the dataframe
    dataframe = pd.read_csv(input_name)

    # Drop the desired rows using the list as reference
    dataframe = dataframe.set_index("event_id")
    for drop_label in drop_labels:
        dataframe.drop(drop_label, inplace=True)
 
    figure, axes = plt.subplots(figsize=(6,6))

    # # Declare axies bounds
    if x_bounds is not None:
        axes.set_xlim(x_bounds)
    if y_bounds is not None:
        axes.set_ylim(y_bounds)

    # Declare axis labels
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    # Plot the total number of nodes (x) vs the total events (y)
    axes.scatter(dataframe[x], dataframe[y], alpha=0.3)

    # Add linear slope text
    line_of_best_fit = stats.linregress(dataframe[x], dataframe[y])
    axes.text(0.5, 0.9, f"Linear Slope: {round(line_of_best_fit.slope,12)}", horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize='x-small')

    # Calculate and plot the quadratic line of best fit using scipy
    if curve_type == "q":
        popt, pcov = curve_fit(quad_func, dataframe[x], dataframe[y])
        a, b, c = popt
        a_str = f"{round(a,12)}x^2 + " if abs(a) > 0.000000000001 else ""
        b_str = f"{round(b,12)}x + " if abs(b) > 0.000000000001  else ""
        c_str = f"{round(c,12)}"
        axes.text(0.5, 0.95, f"Quadratic Model: {a_str}{b_str}{c_str}", horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize='x-small')
        x_fit = np.linspace(min(dataframe[x]), max(dataframe[x]), 100)
        y_fit = quad_func(x_fit, *popt)
        axes.plot(x_fit, y_fit,c='orange')
    # Calculate and plot the linear slope using stats
    elif curve_type == "l":
        axes.text(0.5, 0.95, f"Linear Model: {round(line_of_best_fit.slope,12)}x + {round(line_of_best_fit.intercept,12)}", horizontalalignment='center', verticalalignment='center', transform=axes.transAxes, fontsize='x-small')
        axes.plot(dataframe[x], line_of_best_fit.slope * dataframe[x] + line_of_best_fit.intercept, c='orange')
    else:
        raise ValueError("Incorrect curve type given ...")

    plt.xticks(rotation = 45)
    plt.tight_layout()

    # Plot and save the figure
    plt.savefig(output_name)

# Print a given dataframe from the csv file
def print_from_csv(input_name: str) -> None:
    print(convert_frame(input_name))

# Given a path to a csv, return a constructed pandas dataframe
def csv_to_dataframe(input_name:str) -> pd.DataFrame:
    return pd.read_csv(input_name)

# Return a new dataframe with columns "WALL_TIME and GPU_TIME"
def convert_frame(input_name: str) -> pd.DataFrame:
    dataframe = pd.read_csv(input_name)
    dataframe = dataframe.set_index("event_id")

    # Fetch the mean values row
    mean_series = dataframe.loc["mean"]
    std_series = dataframe.loc["std"]

    if "ml" in input_name:
        labels = ["Metric Learning", "Build Graph", "Filtering", "Preprocess", "InteractionGNN", "ccInfer", "Mean Total Event", "Cumulative Total"]
    elif "mm" in input_name:
        labels = ["Module Map", "Preprocess","InteractionGNN", "ccInfer", "Mean Total", "Cumulative Total"]
    else:
        raise Exception(f"Error: Invalid Path Name {input_name}. Must contain mm or ml to differentiate.")
    
    other_information_labels = ["Edges Before", "Edges After", "Number of Nodes", "r_value", "k_value", "Number of Parameters"]
    
    wall_time = []
    gpu_time = []
    other_information = []

    # Add the mean value time to the correct list (wall_time or gpu_time) as a list of two numbers, so we can still do math on them
    for name, value in mean_series.items():
        if name.endswith("gpu_time") or name == "total_event_gpu":
            gpu_time.append([value, std_series[name]])
        elif name.endswith("time") or name == "total_event":
            wall_time.append([value, std_series[name]])
        elif name == "num_nodes" or name == "7_num_edges_bg" or name == "7_num_edges_fil":
            other_information.append(str(int(value)) + " \u00B1" + str(int(std_series[name])))

    # Calculate the sums of all rows
    wall_time.append([sum([entry[0] for entry in wall_time[:-1]]), sum([entry[1] for entry in wall_time[:-1]])])
    gpu_time.append([sum([entry[0] for entry in gpu_time[:-1]]), sum([entry[1] for entry in gpu_time[:-1]])])

    # Add extra spaces to the information list
    for i in range(len(labels) - len(other_information)):
        other_information.append(" ")

    # Add extra spaces to the information labels
    for i in range(len(labels) - len(other_information_labels)):
        other_information_labels.append(" ")

    # Change the format from two numbers to a formatted string
    for list in [wall_time, gpu_time]:
        for i in range(len(list)):
            list[i] = f"{str(round(list[i][0], 4))} \u00B1 {str(round(list[i][1],4))}"

    # Construct the new dataframe
    if not "cpu" in input_name:
        data = {'':labels, "Wall_Time": wall_time, "GPU_Time": gpu_time, "_": [" " for i in range(len(labels))], " ": other_information_labels, "Other Info": other_information}
    else:
        data = {'':labels, "Wall_Time": wall_time, "_": [" " for i in range(len(labels))], " ": other_information_labels, "Other Information": other_information}
 
    return pd.DataFrame(data)

