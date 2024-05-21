#Importing libraries 
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Convert a given csv file into an excel file with columns "WALL_TIME and GPU_TIME"
def csv_to_excel(input_name, output_name):
    convert_frame(input_name).to_excel(output_name)

# Plot a given csv file to an output file
def plot_points(input_name, output_name):

    #Fetch the dataframe
    dataframe = pd.read_csv(input_name)
    figure, axes = plt.subplots(figsize=(6,6))

    # Declare axis labels
    axes.set_xlabel("Number of nodes")
    axes.set_ylabel("Total time (s)")

    # Plot the total number of nodes (x) vs the total events (y)
    axes.scatter(dataframe["num_nodes"], dataframe["total_event"], alpha=0.3)
    # Calculate and plot the line of best fit
    line_of_best_fit = stats.linregress(dataframe["num_nodes"], dataframe["total_event"])
    axes.plot(dataframe["num_nodes"], line_of_best_fit.slope * dataframe["num_nodes"] + line_of_best_fit.intercept,c='orange')

    plt.xticks(rotation = 45)
    plt.tight_layout()

    # Plot and save the figure
    plt.savefig(output_name)

def plot_edges(input_name, output_name):
    #Fetch the dataframe
    dataframe = pd.read_csv(input_name)
    figure, axes = plt.subplots(figsize=(6,6))

    # Declare axis labels
    axes.set_xlabel("Number of edges")
    axes.set_ylabel("Total time (s)")

    # Plot the total number of edges (x) vs the total events (y)
    axes.scatter(dataframe["7_num_edges_bg"], dataframe["total_event"], alpha=0.3)
    # Calculate and plot the line of best fit
    line_of_best_fit = stats.linregress(dataframe["7_num_edges_bg"], dataframe["total_event"])
    axes.plot(dataframe["7_num_edges_bg"], line_of_best_fit.slope * dataframe["7_num_edges_bg"] + line_of_best_fit.intercept,c='orange')

    plt.xticks(rotation = 45)
    plt.tight_layout()

    # Plot and save the figure
    plt.savefig(output_name, bbox_inches="tight")


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

    # Add the mean value time to the correct list (wall_time or gpu_time)
    for name, value in mean_series.items():
        if name.endswith("gpu_time"):
            gpu_time.append(f"{str(round(value, 4))} \u00B1 {str(round(std_series[name],4))}")
        elif name.endswith("time"):
            wall_time.append(f"{str(round(value, 4))} \u00B1 {str(round(std_series[name],4))}")

    # Construct the new dataframe
    data = {'':labels, "Wall_Time": wall_time, "GPU_Time": gpu_time}
    return pd.DataFrame(data, bbox_inches="tight")

