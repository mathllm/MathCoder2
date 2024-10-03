import json
import os
from tqdm import tqdm
from io import StringIO
import sys
from multiprocessing import Pool
import re

import_path = os.path.abspath(__file__)
import_path = os.path.dirname(import_path)
sys.path.append(import_path)

from python_executor import PythonExecutor
from compute_acc import is_equal


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


executor = None


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
                
                
def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False

    return True


def not_equal(a1, a2):
    try:
        if abs(complex(gt) - complex(output)) > 0.01:
            return True
    except:
        return False
    return False


def execution_result_filter(in_files, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    for in_file in tqdm(in_files):
        out_file = os.path.join(out_dir, "text_" + os.path.basename(in_file))
        if os.path.isfile(out_file):
            continue
        datas = load_jsonl(in_file)
        new_datas = []
        for data in tqdm(datas, desc="processing"):
            text = ""
            for computation in data["computations"]:
                if text != "":
                    text += "\n\n"
                title = computation["title"].strip("*")
                title = re.sub(r"Computation\s*\d*", "", title).strip(" :")
                if title != "":
                    text += title + "\n\n"
                text += f"{computation['conditions']}\n\n{computation['expression']}\n\nresult: {computation['result']}\n\n```python\n{computation['code']}\n```"
            new_datas.append({"idx": data["idx"], "model": data["model"], "text": text})
        save_jsonl(new_datas, out_file)


def main():
    in_dir = "data/mathematical_code_blocks_executed_filtered/correct"
    in_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if file_name.endswith("jsonl")]
    out_dir = "data/mathematical_code"
    execution_result_filter(in_files, out_dir)

    
if __name__ == "__main__":
    main()