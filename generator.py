import os
import glob
import yaml
import graph_generation

output_modes = ["excel", "print", "png"]

class Generator():
    def __init__(self):
        self.output_mode = "print" 
        self.output_dir = ""
        self.input_files = []
        self.command_list = []

    def print_output(self, path: str) -> None:
        print(f"-------------- {path} --------------\n")
        graph_generation.print_from_csv(path)
        print("\n")
        
    def save_to_png(self, path: str) -> None:
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1]) + ".png"
        print(f"Saved {path} to image file {file_name}")
        graph_generation.plot_points(path, file_name)

    def save_to_excel(self, path: str) -> None:
        base_name = os.path.basename(path)
        file_name = self.output_dir + "".join(base_name.split(".")[:-1]) + ".xlsx"
        print(f"Saved {path} to excel file {file_name}")
        graph_generation.csv_to_excel(path, file_name)

    def parse_arguments(self, args: "list[str]") -> "list[str]":
        parsed_args = []
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
                    parsed_args.append([argument, args[i + 1]])
            else:
                if not os.path.exists(argument):
                    raise Exception(f"Path {argument} does not exist.")
                else:
                    parsed_args.append(argument)
            
        self.command_list += parsed_args

    def execute_command(self, command: str, path: str) -> None:
        if command == "--dir":
            if not os.path.exists(path):
                raise Exception(f"The directory {path} does not exist.")
            csv_files = glob.glob(os.path.join(path, "*.csv"))
            self.input_files += csv_files
        elif command == "--file":
            self.input_files.append(path)
        elif command == "--output":
            if path in output_modes:
                self.output_mode = path
            else:
                raise Exception(f"--output must be followed by one of the following: {output_modes}")
        elif command == "--outdir":
            if not os.path.exists(path):
                raise Exception(f"Output dir {path} does not exist")
            self.output_dir = path
        elif command == "--yaml":
            self.get_from_yaml(path)
        elif command == "--help":
            self.print_help()
        else:
            raise Exception(f"Command {command} is not defined.")
            
    def run_command_list(self):
        for entry in self.command_list:
            if isinstance(entry, list):
                self.execute_command(entry[0], entry[1])
            else:
                self.execute_command("--file", entry)

    def process_input_files(self):
        for file in self.input_files:
            if self.output_mode == "print":
                self.print_output(file)
            elif self.output_mode == "excel":
                self.save_to_excel(file)
            elif self.output_mode == "png":
                self.save_to_png(file)

    def print_help(self):
        print("""
    Arguments:
        <file_name>             run on a file 
        --dir <dir_name>        run on all files in a directory
        --file <file_name>      run on a specific file
        --output <output_mode>  choose between printed and excel output
        --help                  see this page again
            """)

    def get_from_yaml(self, yaml_path: str):
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
            for key, value in data.items():
                if isinstance(value, list):
                    for entry in value:
                        self.command_list.append(["--" + key, entry])
                else:
                    self.command_list.append(["--" + key, value])