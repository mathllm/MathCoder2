import json
from tqdm import tqdm
from random import seed, shuffle
import os


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def load_jsonl(in_file):
    with open(in_file, "r", encoding="utf-8") as f:
        datas = [json.loads(line) for line in f]
    return datas


def save_lines(lines, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def write_file_paths_to_txt(in_file, out_dir, n):
    datas = load_jsonl(in_file)
    seed(3407)
    shuffle(datas)
    lines = [data["file_path"] for data in datas]
    step = (len(lines) + n - 1) // n
    for i in range(n):
        save_lines(lines[i * step: i * step + step], os.path.join(out_dir, f"{i}.txt"))


def main():
    in_file = "data/textbooks_orig_pdf_paths/pdf_files_textbooks_filtered_thresh300_jaccard_deduplicated.jsonl"
    out_dir = "data/textbooks_nougat_convert/file_paths"
    n = 30
    write_file_paths_to_txt(in_file, out_dir, n)
    
    
if __name__ == "__main__":
    main()