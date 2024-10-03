import json
from datasets import load_dataset
import re
import os
from tqdm import tqdm


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def get_number(text):
    numbers = re.findall(r'\d', text)
    if len(numbers) == 0:
        return None
    else:
        return numbers[0]


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f: 
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def load_jsonl(path: str):
    datas = []
    with open(path, "r", encoding='utf-8') as f:
        for line in tqdm(f):
            datas.append(json.loads(line))
    return datas


def get_filetered(data_file, type_file, out_file):
    dataset = load_dataset("parquet", data_files=data_file, split="train")
    orig_texts = dataset["text"] # get texts of original dataset file
    datas_type = load_jsonl(type_file)

    datas = []
    pre_idx = -1
    types = []
    for data_type in tqdm(datas_type):
        if pre_idx >= 0 and idx != pre_idx:
            # when all types of devided subtexts has been gathered
            if "1" in types or "2" in types:
                # retrain the text if one of its devided subtexts is type 1 or 2
                datas.append({"text": orig_texts[pre_idx], "idx": pre_idx})
            types = []
        type_number = get_number(data_type["text"])
        types.append(type_number)
        pre_idx = idx
    save_jsonl(datas, out_file)

    
def main():
    data_config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "file_names.json")
    with open(data_config_file, "r") as f:
        data_files = json.load(f)
    
    type_file_dir = "data/open-web-math_Mixtral-8x7B-annotated"
    type_files = [os.path.join(type_file_dir, "classified_" + os.path.basename(data_file)) for data_file in data_files]
    
    out_dir = "data/open-web-math_filtered"
    for data_file, type_file in tqdm(zip(data_files, type_files)):
        if os.path.isfile(data_file) and os.path.isfile(type_file):
            print(data_file)
            print(type_file)
            out_file = os.path.join(out_dir, "math-related_" + os.path.basename(data_file))
            get_filetered(data_file, type_file, out_file)
    

if __name__ == "__main__":
    main()

