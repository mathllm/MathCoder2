import fitz # install using: pip install PyMuPDF
import time
import json
from multiprocessing import Pool
from tqdm import tqdm
import os


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def load_jsonl(in_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            datas.append(json.loads(line))
    return datas


def save_jsonl(data: list, path: str, mode='w', add_timestamp=False, verbose=False) -> None:
    if add_timestamp:
        file_name = f"{path.replace('.jsonl','')}{timestamp()}.jsonl"
    else:
        file_name = path
    with open(file_name, mode, encoding='utf-8') as f:
        if verbose:
            for line in tqdm(data, desc='save'):
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        else:
            for line in data:
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
    

def read_pdf(data):
    pdf_file = data["file_path"]
    text = ""
    try:
        with fitz.open(pdf_file) as doc:
            for page in doc:
                text += page.get_text()
    except:
        pass
    data["pdf_text"] = text
    return data


def jaccard_similarity(string1, string2):
    set1 = set(string1.split())
    set2 = set(string2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0:
        return 0
    return intersection/union
    

def filter_pdf_and_get_text(in_file, out_file):
    """get texts from pdf"""
    fitz.TOOLS.mupdf_display_errors(False)
    
    datas = load_jsonl(in_file)
    
    end = len(datas)
    begin = 0
    if os.path.isfile(out_file):
        begin = len(load_jsonl(out_file))
    counter = begin
    outs = []
    while counter < end:
        pool = Pool(16)
        try:
            results = pool.imap(read_pdf, datas[begin:end])
            for d in tqdm(results, total=len(datas[begin:end])):
                outs.append(d)
                counter += 1
                if counter % 10 == 0 or counter == end:
                    if counter <= 10:
                        save_jsonl(outs, out_file, mode='w', add_timestamp=False, verbose=False)
                    else:
                        save_jsonl(outs, out_file, mode='a', add_timestamp=False, verbose=False)
                    outs = []
                    begin = counter
        except Exception as e:
            print(e)
            print(f'-------Error-------:\n{str(e)}\n-------------------')
            pool.terminate()

        finally:
            pool.close()
            pool.join()


def remove_error_files(in_file, out_file, thresh=0):
    """remove the files whose texts are too short or can't be read by fitz"""
    datas = load_jsonl(in_file)
    print(len(datas))
    new_datas = []
    for data in datas:
        if len(data["pdf_text"]) > thresh and data["dir_name"] != "error":
            new_datas.append(data)
    print(len(new_datas))
    save_jsonl(new_datas, out_file, verbose=True)


def filter_jaccard_similarity_duplicate(in_files, out_file, thresh=0.9, thresh_title=0.5):
    """remove duplicate files with jaccard similarity"""
    datas = []
    if type(in_files) == list:
        for in_file in in_files:
            datas += load_jsonl(in_file)
    else:
        datas = load_jsonl(in_files)
    print("orig length:", len(datas))
    new_datas = []
    for idx, curr_data in tqdm(enumerate(datas)):
        duplicate = False
        for data in datas[:idx]:
            if data["pdf_text"] == curr_data["pdf_text"] or (jaccard_similarity(data["file_name"].lower(), curr_data["file_name"].lower()) > 0.4 and jaccard_similarity(data["pdf_text"], curr_data["pdf_text"]) > thresh):
                duplicate = True
                break
        if not duplicate:
            new_datas.append(curr_data)
    print("deduplicated length:", len(new_datas))
    save_jsonl(new_datas, out_file, verbose=True)


def filter_exact_duplicate(in_files, out_file):
    """filter duplicate files with exact deduplication"""
    datas = []
    if type(in_files) == list:
        for in_file in in_files:
            datas += load_jsonl(in_file)
    else:
        datas = load_jsonl(in_files)
    print("orig length:", len(datas))
    new_datas = []
    for idx, curr_data in tqdm(enumerate(datas)):
        duplicate = False
        for data in datas[:idx]:
            if data["pdf_text"] == curr_data["pdf_text"]:
                duplicate = True
                print(data["file_name"])
                print(curr_data["file_name"])
                break
        if not duplicate:
            new_datas.append(curr_data)
    print("deduplicated length:", len(new_datas))
    save_jsonl(new_datas, out_file, verbose=True)


def get_deduplicated_file_names(in_file, out_file):
    """get titles of the final list of books"""
    datas = load_jsonl(in_file)
    for data in tqdm(datas):
        del data["pdf_text"]
    new_datas = []
    for data in tqdm(datas):
        if data["dir_name"] != "error":
            new_datas.append(data)
    new_datas.sort(key=lambda e: e["file_name"])
    save_jsonl(new_datas, out_file)


def main():
    in_file = "data/textbooks_orig_pdf_paths/pdf_files_textbooks.jsonl"
    out_file = "data/textbooks_orig_pdf_paths/pdf_files_texts_textbooks.jsonl"
    filter_pdf_and_get_text(in_file, out_file)

    
def main_remove():
    in_file = "data/textbooks_orig_pdf_paths/pdf_files_texts_textbooks.jsonl"
    out_file = "data/textbooks_orig_pdf_paths/pdf_files_texts_textbooks_filtered_thresh300.jsonl"
    remove_error_files(in_file, out_file, 300)

    
def main_filter_jaccard():
    in_files = ["data/textbooks_orig_pdf_paths/pdf_files_texts_textbooks_filtered_thresh300.jsonl"]
    out_file = "data/textbooks_orig_pdf_paths/pdf_files_texts_textbooks_filtered_thresh300_jaccard_deduplicated.jsonl"
    filter_jaccard_similarity_duplicate(in_files, out_file, 0.6)


def main_get_file_names():
    in_file = "data/textbooks_orig_pdf_paths/pdf_files_texts_textbooks_filtered_thresh300_jaccard_deduplicated.jsonl"
    out_file = "data/textbooks_orig_pdf_paths/pdf_files_textbooks_filtered_thresh300_jaccard_deduplicated.jsonl"
    get_deduplicated_file_names(in_file, out_file)

    
if __name__ == "__main__":
    main()
    main_remove()
    main_filter_jaccard()
    main_get_file_names()