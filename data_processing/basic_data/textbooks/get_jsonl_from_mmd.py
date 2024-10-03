import json
import os
from tqdm import tqdm
import re


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in tqdm(datas):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def jaccard_similarity(string1, string2):
    set1 = set(string1.split())
    set2 = set(string2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection/union


def have_repititions(text):
    substring = text[-10:]
    substring = re.escape(substring)
    numbers = [i.start() for i in re.finditer(substring, text)] 
    if len(numbers) >= 5 and numbers[-1] - numbers[-2] == numbers[-2] - numbers[-3] and numbers[-2] - numbers[-3] == numbers[-3] - numbers[-4] and numbers[-3] - numbers[-4] == numbers[-4] - numbers[-5]:
        return True
    return False


def line_dedup(text, thresh=0.95):
    lines = text.split("\n\n")
    new_lines = []
    for idx, curr_line in enumerate(lines):
        remove_line = False
        if idx > 0:
            pre_line = lines[idx - 1]
            if pre_line == curr_line or jaccard_similarity(pre_line, curr_line) > thresh:
                remove_line = True
                break
        if (not remove_line) and (not have_repititions(curr_line)):
            new_lines.append(curr_line)
    return "\n\n".join(new_lines)


def get_jsonl_from_mmd(in_dir, out_file):
    files = []
    for dir_path, dir_names, file_names in os.walk(in_dir):
        files.extend([os.path.join(dir_path, file_name) for file_name in file_names if file_name.endswith(".mmd")])
        
    print(f"number of files: {len(files)}")
    
    new_datas = []
    for file in tqdm(files):
        new_data = {}
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            text = re.sub(r"\[MISSING_PAGE_EMPTY:\d+\]\n*", "", text)
            text = re.sub(r"\[MISSING_PAGE_FAIL:\d+\]\n*", "", text)
            text = line_dedup(text, thresh=0.95)
            new_data["text"] = text
        new_data["file_path"] = file
        new_datas.append(new_data)
        
    # out_file = out_file[:-6] + f"_{len(new_datas)}.jsonl"
    save_jsonl(new_datas, out_file)


def main():
    in_dir = "data/textbooks_nougat_convert/converted"
    out_file = "data/textbooks_filtered/textbooks_nougat-converted_final.jsonl"
    get_jsonl_from_mmd(in_dir, out_file)


if __name__ == "__main__":
    main()

