import json
from tqdm import tqdm
import os
from glob import glob


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../.."))


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in tqdm(datas):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def load_jsonl(in_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            datas.append(json.loads(line))
    return datas


def get_filtered_jsonl(in_file, out_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            data = json.loads(line)
            if data["text"] != "":
                datas.append(data)
    save_jsonl(datas, out_file)
        
        
def main():
    in_dir = "data/cc-en-math_filtered-finer_orig"
    out_dir = "data/cc-en-math_filtered-finer"
    in_files = [os.path.join(in_dir, file) for file in os.listdir(in_dir)]
    for in_file in tqdm(in_files):
        print(in_file)
        out_file = os.path.join(out_dir, "simplified_" + os.path.basename(in_file))
        if os.path.isfile(out_file):
            continue
        get_filtered_jsonl(in_file, out_file)
        

if __name__ == "__main__":
    main()