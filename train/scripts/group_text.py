#!/usr/bin/env python3

import os
import random
import shutil
import logging
import transformers
import torch
import json

import numpy as np
import torch.distributed as dist

from datetime import datetime
from dataclasses import field, dataclass
from utils.util import set_logger, print_args

from utils.loader import Processor
from utils.trainer import LoggerCallback, RemoveStateCallback

from transformers.tokenization_utils import AddedToken
from datasets import load_dataset, concatenate_datasets
from transformers import (
    Trainer,
    set_seed,
    AutoConfig,
    AutoTokenizer, 
    HfArgumentParser,
    TrainingArguments, 
    LlamaForCausalLM,
    AutoModelForCausalLM,
    default_data_collator
)


os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


def group_text(tokenizer, out_file, max_len):

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
        
    train_file_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "train_file_names.json")
    with open(train_file_config, "r") as f:
        train_files = json.load(f)
        
    train_sets = []
    for file in train_files:
        print(file)
        _dataset = load_dataset(file.split(".")[-1] if file.split(".")[-1] != "jsonl" else "json", data_files=file, split='train')
        train_sets.append(_dataset)
    
    lengths = np.array([_set.shape[0] for _set in train_sets])
    print(f"Data Lengths: {lengths}")
    train_sets = concatenate_datasets(train_sets)

    process_batch_size = min(1000, len(train_sets))
    
    processor = Processor()
    train_sets = train_sets.shuffle(seed=3407)
    column_names = list(train_sets.features)
    train_sets = train_sets.map(
        processor.group_texts,
        fn_kwargs={
            "tokenizer": tokenizer, 
            "max_len": max_len
        },
        batched=True,
        load_from_cache_file=False,
        remove_columns=column_names,
        batch_size=process_batch_size,
        num_proc=96,
        desc=f"Grouping texts in chunks of {max_len}",
    )
            
    train_sets.to_parquet(out_file)

if __name__ == "__main__":
    model_path = "meta-llama/Meta-Llama-3-8B"
    max_len = 8192
    out_file = "data/tokenized_Meta-Llama-3-8B/grouped.parquet"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    group_text(tokenizer, out_file, max_len)