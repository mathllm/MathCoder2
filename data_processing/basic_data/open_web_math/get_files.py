"""get all files to be processed and save to file_names.json"""


import os
import json


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def create_file_names(in_dir, out_file):
    # Get the list of all files and directories
    dir_list = os.listdir(in_dir)
    file_paths = [os.path.join(in_dir, file_name) for file_name in dir_list]

    # Put into file_paths
    with open(out_file, "w") as f:
        json.dump(file_paths, f)


def main():
    in_dir = "data/open-web-math/data"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    out_file = os.path.join(dir_path, "file_names.json")
    create_file_names(in_dir, out_file)
    

if __name__ == "__main__":
    main()