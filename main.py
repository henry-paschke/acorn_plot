
import sys
from generator import Generator

if __name__ == "__main__":
    gen = Generator()             
    gen.parse_arguments(sys.argv[1:])
    gen.run_command_list()
    gen.process_input_files()