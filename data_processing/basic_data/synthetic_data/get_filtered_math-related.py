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
            
def load_jsonl(in_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            datas.append(json.loads(line))
    return datas
            
def process_text(text):
    first_line = text.split("\n")[0]
    if "revised" in first_line:
        text = text[len(first_line):].strip("\n\t ")
    return text

def get_filetered(in_file, out_file):
    datas = load_jsonl(in_file)
    new_datas = []
    for data in tqdm(datas):
        type_number = data["type_number"]
        text = data["text"]
        if type_number == "1":
            new_datas.append(data)
    save_jsonl(new_datas, out_file)
    
def main():
    in_dir = "data/Education-College-Students_filtered-by-rule_filtered-by-model"
    in_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir)]
    
    out_dir = "data/synthetic_filtered"
    for in_file in in_files:
        if os.path.isfile(in_file):
            print(in_file)
            out_file = os.path.join(out_dir, "math-related_" + os.path.basename(in_file))
            get_filetered(in_file, out_file)

if __name__ == "__main__":
    main()
