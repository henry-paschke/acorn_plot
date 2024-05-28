#Importing libraries 
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Convert a given csv file into an excel file with columns "WALL_TIME and GPU_TIME"
def csv_to_excel(input_name, output_name):
    convert_frame(input_name).to_excel(output_name)

# Plot a given csv file to an output file
def plot_points(input_name, output_name, x, y, x_label = "", y_label = ""):

    # Rows to drop from the dataframe
    drop_labels = ["mean", "std"]

    #Fetch the dataframe
    dataframe = pd.read_csv(input_name)

    # Drop the desired rows using the list as reference
    dataframe = dataframe.set_index("event_id")
    for drop_label in drop_labels:
        dataframe.drop(drop_label, inplace=True)
 
    figure, axes = plt.subplots(figsize=(6,6))

    # Declare axis labels
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    # Plot the total number of nodes (x) vs the total events (y)
    axes.scatter(dataframe[x], dataframe[y], alpha=0.3)
    # Calculate and plot the line of best fit
    line_of_best_fit = stats.linregress(dataframe[x], dataframe[y])
    axes.plot(dataframe[x], line_of_best_fit.slope * dataframe[x] + line_of_best_fit.intercept,c='orange')

    plt.xticks(rotation = 45)
    plt.tight_layout()

    # Plot and save the figure
    plt.savefig(output_name)

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

    if "ml" in input_name:
        labels = ["Metric Learning", "Build Graph", "Filtering", "Preprocess", "InteractionGNN", "ccInfer", "Mean Total", "Cumulative Total"]
    elif "mm" in input_name:
        labels = ["Module Map", "Preprocess","InteractionGNN", "ccInfer", "Mean Total", "Cumulative Total"]
    else:
        raise Exception(f"Error: Invalid Path Name {input_name}. Must contain mm or ml to differentiate.")

    wall_time = []
    gpu_time = []

    # Add the mean value time to the correct list (wall_time or gpu_time) as a list of two numbers, so we can still do math on them
    for name, value in mean_series.items():
        if name.endswith("gpu_time") or name == "total_event_gpu":
            gpu_time.append([value, std_series[name]])
        elif name.endswith("time") or name == "total_event":
            wall_time.append([value, std_series[name]])

    # Calculate the sums of all rows
    wall_time.append([sum([entry[0] for entry in wall_time[:-1]]), sum([entry[1] for entry in wall_time[:-1]])])
    gpu_time.append([sum([entry[0] for entry in gpu_time[:-1]]), sum([entry[1] for entry in gpu_time[:-1]])])

    # Change the format from two numbers to a formatted string
    for list in [wall_time, gpu_time]:
        for i in range(len(list)):
            list[i] = f"{str(round(list[i][0], 4))} \u00B1 {str(round(list[i][1],4))}"

    # Construct the new dataframe
    if not "cpu" in input_name:
        data = {'':labels, "Wall_Time": wall_time, "GPU_Time": gpu_time}
    else:
        data = {'':labels, "Wall_Time": wall_time}
 
    return pd.DataFrame(data)

