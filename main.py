import graph_generation
import sys
import os
import glob
import yaml

input_files = []

output_modes = ["excel", "print", "png"]
output_mode = "print" 
output_dir = ""
command_list = []

def print_output(path: str) -> None:
    print(f"-------------- {path} --------------\n")
    graph_generation.print_from_csv(path)
    print("\n")
    
def save_to_png(path: str) -> None:
    base_name = os.path.basename(path)
    file_name = output_dir + "".join(base_name.split(".")[:-1]) + ".png"
    # JJ magic
    print(f"Saved {path} to image file {file_name}")
    graph_generation.plot_points(path, file_name)

def save_to_excel(path: str) -> None:
    base_name = os.path.basename(path)
    file_name = output_dir + "".join(base_name.split(".")[:-1]) + ".xlsx"
    print(f"Saved {path} to excel file {file_name}")
    graph_generation.csv_to_excel(path, file_name)

def parse_arguments(args: "list[str]") -> "list[str]":
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
        
    return parsed_args

def execute_command(command: str, path: str) -> None:
    global input_files, output_mode, output_dir
    if command == "--dir":
        if not os.path.exists(path):
            raise Exception(f"The directory {path} does not exist.")
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        input_files += csv_files
    elif command == "--file":
        input_files.append(path)
    elif command == "--output":
        if path in output_modes:
            output_mode = path
        else:
            raise Exception(f"--output must be followed by one of the following: {output_modes}")
    elif command == "--outdir":
        if not os.path.exists(path):
            raise Exception(f"Output dir {path} does not exist")
        output_dir = path
        print("output at: " + path)
    elif command == "--yaml":
        get_from_yaml(path)
    elif command == "--help":
        print_help()
    else:
        raise Exception(f"Command {command} is not defined.")
        
def run_command_list(command_list: list):
    for entry in command_list:
        if isinstance(entry, list):
            execute_command(entry[0], entry[1])
        else:
            execute_command("--file", entry)

def process_input_files():
    for file in input_files:
        if output_mode == "print":
            print_output(file)
        elif output_mode == "excel":
            save_to_excel(file)
        elif output_mode == "png":
            save_to_png(file)

def print_help():
    print("""
Arguments:
    <file_name>             run on a file 
    --dir <dir_name>        run on all files in a directory
    --file <file_name>      run on a specific file
    --output <output_mode>  choose between printed and excel output
    --help                  see this page again
          """)

def get_from_yaml(yaml_path: str):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
        for key, value in data.items():
            if isinstance(value, list):
                for entry in value:
                    command_list.append(["--" + key, entry])
            else:
                command_list.append(["--" + key, value])
                    

command_list += parse_arguments(sys.argv[1:])
run_command_list(command_list)
process_input_files()