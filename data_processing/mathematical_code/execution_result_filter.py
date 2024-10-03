import json
import os
from tqdm import tqdm
from io import StringIO
import sys
from multiprocessing import Pool

import_path = os.path.abspath(__file__)
import_path = os.path.dirname(import_path)
sys.path.append(import_path)

from compute_acc import is_equal


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


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
        if abs(complex(a1) - complex(a2)) > 0.01:
            return True
    except:
        return False
    return False


def execution_result_filter(in_files, out_dir):
    out_dir_correct = os.path.join(out_dir, "correct")
    out_dir_wrong = os.path.join(out_dir, "wrong")
    if not os.path.exists(out_dir_correct):
        os.makedirs(out_dir_correct)
    if not os.path.exists(out_dir_wrong):
        os.makedirs(out_dir_wrong)
    for in_file in tqdm(in_files):
        out_file_correct = os.path.join(out_dir_correct, "correct_" + os.path.basename(in_file))
        out_file_wrong = os.path.join(out_dir_wrong, "wrong_" + os.path.basename(in_file))
        if os.path.isfile(out_file_correct):
            continue
        datas = load_jsonl(in_file)
        correct_datas = []
        wrong_datas = []
        for data in tqdm(datas, desc="processing"):
            correct_computations = []
            wrong_computations = []
            for computation in data["computations"]:
                gt = computation["result"]
                error = computation["execution_error"]
                output = computation["execution_output"]
                if error != "" or (len(gt) < 20 and is_number(gt) and is_number(output) and not_equal(gt, output)):
                    wrong_computations.append(computation)
                else:
                    correct_computations.append(computation)
            if len(correct_computations) > 0:
                correct_datas.append({"idx": data["idx"], "model": data["model"], "computations": correct_computations})
            if len(wrong_computations) > 0:
                wrong_datas.append({"idx": data["idx"], "model": data["model"], "computations": wrong_computations})
        save_jsonl(correct_datas, out_file_correct)
        save_jsonl(wrong_datas, out_file_wrong)


def main():
    in_dir = "data/mathematical_code_blocks_executed"
    in_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if file_name.endswith("jsonl")]
    out_dir = "data/mathematical_code_blocks_executed_filtered"
    execution_result_filter(in_files, out_dir)


if __name__ == "__main__":
    main_cc_en()