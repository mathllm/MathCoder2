import json
import os
from tqdm import tqdm
from io import StringIO
import sys
from multiprocessing import Pool
from argparse import ArgumentParser

import_path = os.path.abspath(__file__)
import_path = os.path.dirname(import_path)
sys.path.append(import_path)

from python_executor import PythonExecutor


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


def add_execution_result(example):
    global executor
    computation = example["computation"]
    output, metadata = executor.apply(computation["code"])
    computation["execution_error"] = metadata["concise_exec_info"]
    computation["execution_output"] = output
    return example


def execute_code_files(in_files, out_dir):
    global executor
    executor = PythonExecutor(get_answer_from_stdout=True)
    for in_file in tqdm(in_files):
        out_file = os.path.join(out_dir, "executed_" + os.path.basename(in_file))
        if os.path.isfile(out_file):
            continue
        datas = load_jsonl(in_file)
        
        datas_flattened = []
        for i, data in tqdm(enumerate(datas)):
            for j, computation in enumerate(data["computations"]):
                datas_flattened.append({"computation": computation, "i": i, "j": j})
        print("datas len: ", len(datas))
        print("datas_flattened len: ", len(datas_flattened))

        batch_size = 100000
        for idx in tqdm(range(0, len(datas_flattened), batch_size)):
            batch_code = [e["computation"]["code"] for e in datas_flattened[idx: idx + batch_size]]
            batch_result = executor.batch_apply(batch_code)
            for result, data_flattened in zip(batch_result, datas_flattened[idx: idx + batch_size]):
                datas[data_flattened["i"]]["computations"][data_flattened["j"]]["execution_output"] = result[0].strip("\n\t ")
                datas[data_flattened["i"]]["computations"][data_flattened["j"]]["execution_error"] = result[1]["concise_exec_info"].strip("\n\t ")
        save_jsonl(datas, out_file)


def main():
    in_dir = "data/mathematical_code_blocks"
    in_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if file_name.endswith("jsonl")]
    out_dir = "data/mathematical_code_blocks_executed"
    execute_code_files(in_files, out_dir)


if __name__ == "__main__":
    main()