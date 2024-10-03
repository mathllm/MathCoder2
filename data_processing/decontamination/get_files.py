import json
import os


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


def get_files(in_dirs, out_file):
    file_names = []
    for in_dir in in_dirs:
        file_names.extend([os.path.join(in_dir, file) for file in os.listdir(in_dir)])
    print(len(file_names))

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(file_names, f)


def main():
    in_dirs = [
        "data/open-web-math_filtered",
        "data/cc-en-math_filtered-finer",
        "data/jupyter-script_filtered",
        "data/jupyter-structured_filtered",
        "data/python_filtered",
        "data/synthetic_filtered",
        "data/textbooks_filtered",
        "data/mathematical_code",
    ]
    out_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "file_names.json")
    get_files(in_dirs, out_file)


if __name__ == "__main__":
    main()