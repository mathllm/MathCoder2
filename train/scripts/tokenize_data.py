import json
import os
import sys
from transformers import AutoTokenizer
from datasets import load_dataset
from tqdm import tqdm
from argparse import ArgumentParser

from utils.loader import Processor


os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


def load_jsonl(in_file):
    with open(in_file, "r", encoding="utf-8") as f:
        datas = [json.loads(line) for line in f]
    return datas


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def prosess_tokenize(in_file, out_dir, tokenizer):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_file = os.path.join(out_dir, "tokenized_" + "-".join(os.path.basename(in_file).split(".")[:-1]) + ".parquet")
    if os.path.isfile(out_file):
        return
    processor = Processor()
    _dataset = load_dataset(in_file.split(".")[-1] if in_file.split(".")[-1] != "jsonl" else "json", data_files=in_file, split='train')
    if "text" not in _dataset.features:
        _dataset = _dataset.rename_column("output", "text")
    columns_to_remove = [feature for feature in _dataset.features if feature != "text"]
    _dataset = _dataset.remove_columns(columns_to_remove)
    process_batch_size = min(200, len(_dataset))
    column_names = list(_dataset.features)
    _dataset = _dataset.map(
        processor.process_tokenize,
        fn_kwargs={
            "tokenizer": tokenizer, 
        },
        batched=True,
        load_from_cache_file=False,
        remove_columns=column_names,
        batch_size=process_batch_size,
        num_proc=64,
        desc="Running tokenizer on dataset",
    )
    _dataset.to_parquet(out_file)


def main():
    model_path = "meta-llama/Meta-Llama-3-8B"
    out_dir = "data/tokenized_Meta-Llama-3-8B/data"
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_file = os.path.join(dir_path, "file-names_to-be-tokenized.json")
    with open(data_file, "r") as f:
        data_files = json.load(f)

    for in_file in data_files:
        prosess_tokenize(in_file, out_dir, tokenizer)
        

if __name__ == "__main__":
    main_parquet1()
