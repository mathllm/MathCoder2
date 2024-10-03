import os
import json


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def get_files_in_dir(in_dirs, suffix, out_file):
    files = []
    for in_dir in in_dirs:
        for dir_path, dir_names, file_names in os.walk(in_dir):
            for file_name in file_names:
                if file_name.endswith(suffix) and os.path.basename(dir_path) != "error":
                files.append({"file_name": file_name, "dir_name": os.path.basename(dir_path), "file_path": os.path.join(dir_path, file_name)})
    save_jsonl(files, out_file)


def main():
    in_dirs = ["data/textbooks_pdf"]
    suffix = ".pdf"
    out_file = "data/textbooks_orig_pdf_paths/pdf_files_textbooks.jsonl"
    get_files_in_dir(in_dirs, suffix, out_file)


if __name__ == "__main__":
    main()