import json
from tqdm import tqdm
import random
import os


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../.."))


def load_jsonl(in_file, weight=1):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            if random.random() < weight:
                datas.append(json.loads(line))
    return datas


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in tqdm(datas):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

      
def sample(in_files, out_file, weight, n):
    """sample for n data points with possibility of weight"""
    datas = []
    cnt = 0
    for in_file in tqdm(in_files):
        datas.extend(load_jsonl(in_file, weight))
        cnt += 1
        if cnt >= n:
            break
    save_jsonl(datas, out_file)


def create_train(in_files, labels, out_file):
    """create train and test file for fasttext, in_files and labels are matched sequentially"""
    new_datas = []
    for in_file, label in zip(in_files, labels):
        datas = load_jsonl(in_file)
        for data in datas:
            new_datas.append({'label': label, 'text': data["text"].replace("\n", " ")})
    random.shuffle(new_datas)
    print(len(new_datas))
    len_test = len(new_datas) // 1000
    with open(out_file[:-4] + "_train.txt", "w", encoding="utf-8") as f:
        for data in tqdm(new_datas[: - len_test]):
            f.write(f"__label__{data['label']} {data['text']}\n")
    with open(out_file[:-4] + "_test.txt", "w", encoding="utf-8") as f:
        for data in tqdm(new_datas[ - len_test:]):
            f.write(f"__label__{data['label']} {data['text']}\n")
            

def main_sample_other():
    in_dirs = [
        "data/cc-en"
    ]
    in_files = []
    for in_dir in in_dirs:
        in_files.extend([os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if (file_name.endswith("json") or file_name.endswith("jsonl")) and not file_name.startswith("setting")])
    print(in_files)
    out_file = "data/fasttext_filter-cc-en/other.jsonl"
    weight = 0.02
    sample(in_files, out_file, weight)

    
def main_train():
    in_files = [
        "data/fasttext_filter-cc-en/other.jsonl",
    ]
    labels = [
        "other",
    ]

    math_dir = "data/open-web-math_filtered"
    math_files = [os.path.join(math_dir, file_name) for file_name in os.listdir(math_dir)]
    
    in_files += math_files
    labels += ["math" for _ in range(len(math_files))]

    out_file = "data/fasttext_filter-cc-en/math-vs-other.txt"
    create_train(in_files, labels, out_file)
    

    
if __name__ == "__main__":
    main_sample_other()
    main_train()