import os
import glob
import yaml
import graph_generation

class Plotter():
    """
    A graph plotting command system for command line interface or direct use in a script.
    """
    output_modes = ["excel", "print", "png"]

    def __init__(self):
        self.output_mode = "print" 
        self.output_dir = ""
        self.input_dir = ""
        self.input_files = []
        self.command_list = []

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
            if argument.startswith("--"):
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
    def parse_yaml(self, yaml_path: str):
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
            for key, value in data.items():
                if isinstance(value, list):
                    for entry in value:
                        self.command_list.append(["--" + key, entry])
                else:
                    self.command_list.append(["--" + key, value])

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
        elif command == "--yaml":
            self.parse_yaml(argument)
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
        if mode in self.output_modes:
            self.output_mode = mode
        else:
            raise Exception(f"--output must be followed by one of the following: {self.output_modes}")

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
        
    """
    Saves the graph of one given csv to a png file
    """
    def save_to_png(self, path: str) -> None:
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1])

        points_name =  file_name + "_points.png"
        print(f"Saved {path} to image file {points_name}")
        graph_generation.plot_points(path, points_name)

        edges_name =  file_name + "_edges.png"
        print(f"Saved {path} to image file {edges_name}")
        graph_generation.plot_edges(path, edges_name)

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
        for entry in self.command_list:
            if isinstance(entry, list):
                self.execute_command(entry[0], entry[1])
            else:
                self.execute_command("--file", entry)
        self.command_list.clear()

    """
    Processes all the files in the file queue according to the current output mode
    """
    def process_file_queue(self):
        for file in self.input_files:
            if self.output_mode == "print":
                self.print_output(file)
            elif self.output_mode == "excel":
                self.save_to_excel(file)
            elif self.output_mode == "png":
                self.save_to_png(file)
        self.input_files.clear()

    """
    Processes all the queues.
    """
    def process(self):
        self.run_command_queue()
        self.process_file_queue()