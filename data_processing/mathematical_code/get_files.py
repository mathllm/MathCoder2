import os
import json
from tqdm import tqdm


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


def load_jsonl(in_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="load"):
            datas.append(json.loads(line))
    return datas


def save_jsonl(data: list, path: str, mode='w', verbose=True) -> None:
    file_name = path
    with open(file_name, mode, encoding='utf-8') as f:
        if verbose:
            for line in tqdm(data, desc='save'):
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        else:
            for line in data:
                f.write(json.dumps(line, ensure_ascii=False) + '\n')


def create_file_names(in_dirs, out_file):
    # Get the list of all files and directories
    file_paths = []
    for in_dir in in_dirs:
        dir_list = os.listdir(in_dir)
        file_paths.extend([os.path.join(in_dir, file_name) for file_name in dir_list])

    # Put into file_paths
    with open(out_file, "w") as f:
        json.dump(file_paths, f)


def create_file_names_finished_unfinished(in_files, target_dir, out_file_finished, out_file_unfinished):
    files_unfinished = []
    files_finished = []
    for in_file in in_files:
        target_file = os.path.join(target_dir, "computation-code_" + os.path.basename(in_file))
        if not os.path.isfile(target_file):
            files_unfinished.append(target_file)
            print(in_file)
        else:
            target_datas = load_jsonl(target_file)
            in_datas = load_jsonl(in_file)
            if len(in_datas) > len(target_datas):
                files_unfinished.append(target_file)
                print(in_file)
            else:
                files_finished.append(target_file)
    
    with open(out_file_finished, "w") as f:
        json.dump(files_finished, f)
    with open(out_file_unfinished, "w") as f:
        json.dump(files_unfinished, f)


def main():
    in_dirs = [
        "data/open-web-math_filtered",
        "data/cc-en-math_filtered-finer",
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    out_file = os.path.join(dir_path, "file_names.json")
    create_file_names(in_dirs, out_file)

    
if __name__ == "__main__":
    main()