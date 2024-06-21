import os
import glob
import yaml
import graph_generation
from typing import Tuple

class Plotter():
    """
    A graph plotting command system for command line interface or direct use in a script.
    """
    availible_output_modes = ["excel", "print", "png", "png_evn", "png_mem"]

    def __init__(self):
        self.output_modes = []
        self.output_dir = ""
        self.input_dir = ""
        self.input_files = []
        self.command_list = []
        self.bounds = []
        self.regexes = []

    # Parsing methods

    """
    Parses a list of arguments and adds them to the command queue.
    """
    def parse_arguments(self, args: "list[str]") -> "list[str]":
        next_arg_skipped = False
        for i in range(len(args)):
            if next_arg_skipped:
                next_arg_skipped = False
                continue
            argument = args[i]
            if argument == "--help":
                self.command_list.append([argument, None])
            elif argument.startswith("--"):
                if i + 1 > len(args):
                    raise Exception(f"Option {argument} must be followed by an argument.")
                else:
                    next_arg_skipped = True
                    self.command_list.append([argument, args[i + 1]])
            else:
                if not os.path.exists(argument):
                    raise Exception(f"Path {argument} does not exist.")
                else:
                    self.command_list.append(argument)

    """
    Parses a yaml file and adds its commands to the command queue.
    """
    def parse_yaml(self, yaml_path: str) -> list:
        l = []
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
            for key, value in data.items():
                if isinstance(value, list):
                    for entry in value:
                        l.append(["--" + key, entry])
                else:
                    l.append(["--" + key, value])
        return l

    # Command runner for text commands

    """
    Executes a text command and its argument. 
    """
    def execute_command(self, command: str, argument: str) -> None:
        if command == "--dir":
            self.add_directory(argument)
        elif command == "--file":
            self.add_file(argument)
        elif command == "--output":
            self.set_output_mode(argument)
        elif command == "--indir":
            self.set_input_dir(argument)
        elif command == "--outdir":
            self.set_output_dir(argument)
        elif command == "--alldir":
            self.add_directory(argument)
            self.set_output_dir(argument)
        elif command == "--bounds":
            self.set_bounds(argument)
        elif command == "--regex":
            self.add_regex(argument)
        elif command == "--help":
            self.print_help()
        else:
            raise Exception(f"Command {command} is not defined.")

    # Command implementations
        
    """
    Adds all csvs in a directory to the file queue.
    """
    def add_directory(self, path):
        path = self.input_dir + path
        if not os.path.exists(path):
            raise Exception(f"The directory {path} does not exist.")
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        self.input_files += csv_files
    
    """
    Adds one file to the file queue.
    """
    def add_file(self, path: str):
        path = self.input_dir + path
        if not os.path.exists(path):
            raise Exception(f"File {path} does not exist")
        if path not in self.input_files:
            self.input_files.append(path)

    """
    Sets the input directory for all future file additions.
    """
    def set_input_dir(self, path: str):
        if not os.path.exists(path):
            raise Exception(f"Input dir {path} does not exist")
        self.input_dir = path

    """
    Sets the output directory for all future file outputs.
    """
    def set_output_dir(self, path: str):
        if not os.path.exists(path):
            print(f"Creating {path} because it does not exist.")
            os.makedirs(path)
        self.output_dir = path

    """
    Sets the output mode. May be one of the following:
        - png
        - print
        - excel
    """
    def set_output_mode(self, mode: str):
        if mode in self.availible_output_modes:
            self.output_modes.append(mode)
        elif mode == "all":
            self.output_modes = self.availible_output_modes
            self.output_modes.remove("png_mem")
        else:
            raise Exception(f"--output must be followed by one of the following: {self.availible_output_modes}")
        
    def set_bounds(self, bounds: float):
        self.bounds.append(float(bounds))

    def add_regex(self, regex: str):
        regx = regex.split("=")[0].strip()
        command = regex.split("=")[1].strip()
        command_name = "--" + command.split("(")[0].strip()
        command_parameter = (command.split("(")[1]).split(")")[0].strip()
        if command_parameter.isnumeric():
            command_parameter = float(command_parameter)
        self.regexes.append([regx, command_name, command_parameter])
        

    """
    Prints the command line help output.
    """
    def print_help(self):
        print("""
    Arguments:
        <file_name>             run on a file 
        --dir <dir_name>        run on all files in a directory
        --file <file_name>      run on a specific file
        --output <output_mode>  choose between printed, excel, and png output
        --indir <dir>           sets the input directory
        --outdir <dir>          sets the output directory
        --alldir <dir>          sets the base folder where all files exist and will be created
        --yaml <yaml_file_path> loads a yaml configuration and overrides existing settings according to its system
        --bounds <x>            sets the y bounds from 0 to x. Using twice will set the y lower and upper (Will be refactored in the future to use tuple)
        --regex <regex>         sets a regex, where regex is <file_name_regex = function_to_use( argument )>
        --help                  see this page again
            """)

    # Methods of outputting the final data

    """
    Prints the graph of one given csv
    """
    def print_output(self, path: str) -> None:
        print(f"-------------- {path} --------------\n")
        graph_generation.print_from_csv(path)
        print("\n")

    def calculate_bounds(self):
        """
        Uses the list of bounds to get a list of 2 tuples for bounds
        """
        if len(self.bounds) == 0:
            return [None, None]
        elif len(self.bounds) == 1:
            return [None, (0, self.bounds[0])]
        elif len(self.bounds) == 2:
            return [None, (self.bounds[0], self.bounds[1])]
        elif len(self.bounds) == 3:
            raise Exception("3 Bounds only is not supported.")
        elif len(self.bounds) == 4:
            return [(self.bounds[0], self.bounds[1]), (self.bounds[2], self.bounds[3])]
        
    def check_regexes(self, name):
        for regex in self.regexes:
            if regex[0] in name:
                return True
        return False
        
    """
    Saves the graph of one given csv to a png file
    """
    def save_to_png(self, path: str) -> None:
        if "memory" in path:
            self.save_to_png_mem(path)
            pass
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1])

        bounds = self.calculate_bounds()

        points_name =  file_name + "_points"
        for type in ["q", "l"]:
            graph_generation.plot_points(path, points_name + "_" + type, "num_nodes", "total_event", "Number of nodes", "Total time (s)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {points_name}_{type}.png")
            graph_generation.plot_points(path, points_name + "_" + type, "num_nodes", "total_event", "Number of nodes", "Total time (s)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {points_name}_{type}.png")

        edges_name =  file_name + "_edges"
        for type in ["q", "l"]:
            graph_generation.plot_points(path, edges_name + "_" + type, "7_num_edges_bg", "total_event", "Number of edges", "Total time (s)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {edges_name}_{type}.png")
            graph_generation.plot_points(path, edges_name + "_" + type, "7_num_edges_bg", "total_event", "Number of edges", "Total time (s)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {edges_name}_{type}.png")

    def save_to_png_evn(self, path: str):
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1])

        bounds = self.calculate_bounds()
        name =  file_name + "_edges_vs_nodes"
        for type in ["q", "l"]:
            graph_generation.plot_points(path, name + "_" + type, "num_nodes", "7_num_edges_bg", "Number of nodes", "Number of edges", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {name}_{type}.png")

    def save_to_png_mem(self, path: str):
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1])

        bounds = self.calculate_bounds()

        nodes_name =  file_name + "_mem_vs_nodes"
        for type in ["q", "l"]:
            graph_generation.plot_points(path, nodes_name + "_" + type, "num_nodes", "peak_memory", "Number of nodes", "Peak memory (GB)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {nodes_name}_{type}.png")
            graph_generation.plot_points(path, nodes_name + "_" + type, "num_nodes", "peak_memory", "Number of nodes", "Peak memory (GB)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {nodes_name}_{type}.png")

        edges_name =  file_name + "_mem_vs_edges"
        for type in ["q", "l"]:
            graph_generation.plot_points(path, edges_name + "_" + type, "num_edges_bg", "peak_memory", "Number of edges", "Peak memory (GB)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {edges_name}_{type}.png")
            graph_generation.plot_points(path, edges_name + "_" + type, "num_edges_bg", "peak_memory", "Number of edges", "Peak memory (GB)", bounds[0], bounds[1], type)
            print(f"Saved {path} to image file {edges_name}_{type}.png")



    """
    Saves the graph of one given csv to an excel file
    """
    def save_to_excel(self, path: str) -> None:
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1]) + ".xlsx"
        print(f"Saved {path} to excel file {file_name}")
        graph_generation.csv_to_excel(path, file_name)

    # Processing methods

    """
    Runs all the commands in the command queue
    """
    def run_command_queue(self):
        for i in range(len(self.command_list)):
            yaml_file = None
            entry = self.command_list.copy()[i]
            if isinstance(entry, list):
                if entry[0] == "--yaml":
                    yaml_file = entry[1]
                else:
                    continue
            elif entry.endswith(".yaml"):
                yaml_file = entry
            self.command_list[i: i+1] = self.parse_yaml(yaml_file)
            
        for entry in self.command_list:
            if isinstance(entry, list):
                self.execute_command(entry[0], entry[1])
            else:
                if entry.endswith(".csv"):
                    self.execute_command("--file", entry)
                else:
                    raise Exception(f"Cannot infer an action for file {entry}")
        self.command_list.clear()

    def process_file(self, file):
        for mode in self.output_modes:
            if mode == "print":
                self.print_output(file)
            elif mode == "excel":
                self.save_to_excel(file)
            elif mode == "png":
                self.save_to_png(file)
            elif mode == "png_evn":
                self.save_to_png_evn(file)
            elif mode == "png_mem":
                self.save_to_png_mem(file)

    """
    Processes all the files in the file queue according to the current output mode
    """
    def process_file_queue(self):
        if len(self.output_modes) == 0:
            self.output_modes.append("print")
        for file in self.input_files.copy():
            if not self.check_regexes(file):
                self.process_file(file)
                self.input_files.remove(file)
        for regex in self.regexes:
            self.execute_command(regex[1], regex[2])
            for file in self.input_files.copy():
                if regex[0] in file:
                    self.process_file(file)
                    self.input_files.remove(file)    

        self.input_files.clear()

    """
    Processes all the queues.
    """
    def process(self):
        self.run_command_queue()
        self.process_file_queue()