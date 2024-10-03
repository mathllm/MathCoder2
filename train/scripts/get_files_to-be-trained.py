import os
import json


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


def create_file_names(in_dirs, out_file):
    # Get the list of all files and directories
    file_paths = []
    for in_dir in in_dirs:
        dir_list = os.listdir(in_dir)
        file_paths.extend([os.path.join(in_dir, file_name) for file_name in dir_list])

    # Put into file_paths
    with open(out_file, "w") as f:
        json.dump(file_paths, f)


def main_train():
    in_dirs = ["data/tokenized_Meta-Llama-3-8B/data"]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    out_file = os.path.join(dir_path, "file_names_to-be-trained.json")
    create_file_names(in_dirs, out_file)


if __name__ == "__main__":
    print(os.getcwd())