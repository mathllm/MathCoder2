import json
import os
from tqdm import tqdm
import re
from random import shuffle, seed


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../.."))


def load_jsonl(in_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="load"):
            datas.append(json.loads(line))
    return datas

def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in tqdm(datas, desc="save"):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
def get_number(text):
    numbers = re.findall(r'\d', text)
    if len(numbers) == 0:
        return None
    else:
        return numbers[-1]


def devide_math_related_and_unrelated(classify_file, data_file, related_file, unrelated_file):
    classify_datas = load_jsonl(classify_file)
    datas = load_jsonl(data_file)
    related_datas = []
    unrelated_datas = []
    for idx, classify_data in tqdm(enumerate(classify_datas)):
        data = datas[idx]
        type_number = get_number(classify_data["type"])
        if type_number == "1" or type_number == "2":
            related_datas.append(data)
        else:
            unrelated_datas.append(data)
    save_jsonl(related_datas, related_file)
    save_jsonl(unrelated_datas, unrelated_file)


def get_train_test(related_dir, unrelated_dir, train_file, test_file):
    seed(3407)
    related_datas = []
    related_files = [os.path.join(related_dir, file_name) for file_name in os.listdir(related_dir)]
    for related_file in tqdm(related_files):
        related_datas += load_jsonl(related_file)
    print(len(related_datas))
    unrelated_datas = []
    unrelated_files = [os.path.join(unrelated_dir, file_name) for file_name in os.listdir(unrelated_dir)]
    for unrelated_file in tqdm(unrelated_files):
        unrelated_datas += load_jsonl(unrelated_file)
    shuffle(unrelated_datas)
    print(len(unrelated_datas))
    lines = []
    for related_data in tqdm(related_datas):
        text = related_data['text'].replace('\n', ' ')
        lines.append(f"__label__related {text}")
    for unrelated_data in tqdm(unrelated_datas[:len(related_datas)]):
        text = unrelated_data['text'].replace('\n', ' ')
        lines.append(f"__label__unrelated {text}")
    shuffle(lines)
    num_test = len(lines) // 10000
    with open(train_file, "w", encoding="utf-8") as f:
        for line in tqdm(lines[:-num_test], desc="write"):
            f.write(line + "\n")
    with open(test_file, "w", encoding="utf-8") as f:
        for line in tqdm(lines[-num_test:], desc="write"):
            f.write(line + "\n")


def main_devide():
    in_dir = "data/cc-en-math_filtered_annotated"
    prefix = "classified_"
    classify_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if file_name.startswith(prefix)]
    data_dir = "data/cc-en-math_filtered"
    related_dir = "data/cc-en-math_filtered_devided/related"
    unrelated_dir = "data/cc-en-math_filtered_devided/unrelated"
    for classify_file in tqdm(classify_files):
        data_file = os.path.join(data_dir, os.path.basename(classify_file).replace(prefix, ""))
        related_file = os.path.join(related_dir, "related_" + os.path.basename(classify_file))
        unrelated_file = os.path.join(unrelated_dir, "unrelated_" + os.path.basename(classify_file))
        devide_math_related_and_unrelated(classify_file, data_file, related_file, unrelated_file)


def main_get_train_test():
    related_dir = "data/cc-en-math_filtered_devided/related"
    unrelated_dir = "data/cc-en-math_filtered_devided/unrelated"
    train_file = "data/fasttext_filter-finer-cc-en/related-vs-unrelated_train.txt"
    test_file = "data/fasttext_filter-finer-cc-en/related-vs-unrelated_test.txt"
    get_train_test(related_dir, unrelated_dir, train_file, test_file)
    
    
if __name__ == "__main__":
    main_devide()
    main_get_train_test()