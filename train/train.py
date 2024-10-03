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

logger = logging.getLogger()

@dataclass
class DataArguments:

    no_timestamps: bool = field(default=False)
    no_load_model_pararmeters: bool = field(default=False)
    
    resume_step: int = field(default=None)
    resume_batch_size: int = field(default=None)

    # data
    train_parquet_file: str = field(default=None)
    train_file_config: str = field(default=None)
    train_dataset: str = field(default=None)
    train_coef: str = field(default=None)
    delete_long_sample: bool = field(default=False)

    # process
    max_len: int = field(default=2048)
    preprocessing_num_workers: int = field(default=64)
    
    # model
    model_cfg: str = field(default="data/models/starcoder")
    flash_attention: bool = field(default=False)

    resume_from: str = field(default=None)

    # output
    stream: bool = field(default=False)


def train():
    parser = HfArgumentParser((DataArguments, TrainingArguments))

    data_args, training_args = parser.parse_args_into_dataclasses()

    training_args._frozen = False

    if not data_args.no_timestamps:
        timestr = datetime.now().strftime("-%m%d%H%M")
        training_args.output_dir = training_args.output_dir + timestr

    training_args.logging_dir = os.path.join(training_args.output_dir, 'logging')

    if os.path.exists(training_args.output_dir):
        if training_args.overwrite_output_dir:
            if training_args.process_index == 0:
                shutil.rmtree(training_args.output_dir)
        else:
            raise ValueError(f"Output directory ({training_args.output_dir}) already exists. Use --overwrite_output_dir to overcome.")
    
    if training_args.world_size > 1:
        dist.barrier()
    
    if training_args.process_index == 0:
        os.makedirs(training_args.output_dir)
    
    if training_args.world_size > 1:
        dist.barrier()
    
    set_seed(training_args.seed)

    node_rank = int(os.getenv('GROUP_RANK', '0'))

    for _logger in [logger, transformers.utils.logging.get_logger(), logging.getLogger('DeepSpeed')]:
        set_logger(_logger, training_args.local_rank, data_args.stream, os.path.join(training_args.output_dir, f'log-node-{node_rank}.log'))

    logger.warning("Device: %s, rank: %s, world size: %s", training_args.device, training_args.process_index, training_args.world_size)

    if training_args.world_size > 1:
        dist.barrier()

    print_args(data_args, 'Data Arguments')
    print_args(training_args, 'Training Arguments')

    processor = Processor()

    config = AutoConfig.from_pretrained(data_args.model_cfg, trust_remote_code=True)
    config._attn_implementation = "flash_attention_2"
    config.use_cache = False

    if data_args.no_load_model_pararmeters:
        model = AutoModelForCausalLM.from_config(config, trust_remote_code=True)
    else:
        model = AutoModelForCausalLM.from_pretrained(data_args.model_cfg, config=config, torch_dtype=torch.bfloat16, trust_remote_code=True)
    # tokenizer = AutoTokenizer.from_pretrained(data_args.model_cfg, legacy=False, use_fast=True)
    tokenizer = AutoTokenizer.from_pretrained(data_args.model_cfg, trust_remote_code=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
        
    if data_args.train_parquet_file is not None:
        train_sets = load_dataset("parquet", data_files=data_args.train_parquet_file, split='train')
    elif data_args.train_file_config is not None:
        with open(data_args.train_file_config, "r") as f:
            train_files = json.load(f)
            
        train_sets = []
        for file in train_files:
            _dataset = load_dataset(file.split(".")[-1] if file.split(".")[-1] != "jsonl" else "json", data_files=file, split='train')
            train_sets.append(_dataset)
        
        lengths = np.array([_set.shape[0] for _set in train_sets])
        logger.info("Data Lengths: %s", lengths)

        for i in range(1, len(train_sets)):
            train_sets[i] = train_sets[i].cast(train_sets[0].features)

        train_sets = concatenate_datasets(train_sets)
    else:
        raise ValueError("Should provide either 'train_dataset' or 'train_file_config'")
    
    logger.info('Total %d case', len(train_sets))

    process_batch_size = min(1000, len(train_sets))
    
    with training_args.main_process_first(desc="Log a few random samples from the training set"):
        for index in random.sample(range(len(train_sets)), 3):
            logger.info(
                "Sample %d of the raw training set:\n\ninput_tokens: %s\n\n%s",
                index, 
                train_sets[index]['input_ids'],
                tokenizer.convert_ids_to_tokens(train_sets[index]['input_ids']), 
            )
    
    train_sets = train_sets.shuffle(seed=training_args.seed)
    column_names = list(train_sets.features)
    if data_args.train_parquet_file is None:
        with training_args.main_process_first(desc="dataset map grouping"):
            train_sets = train_sets.map(
                processor.group_texts,
                fn_kwargs={
                    "tokenizer": tokenizer, 
                    "max_len": data_args.max_len
                },
                batched=True,
                load_from_cache_file=False,
                remove_columns=column_names,
                batch_size=process_batch_size,
                num_proc=data_args.preprocessing_num_workers,
                desc=f"Grouping texts in chunks of {data_args.max_len}",
            )
    
        with training_args.main_process_first(desc="Log a few random samples from the grouped training set"):
            for index in random.sample(range(len(train_sets)), 3):
                logger.info(
                    "Sample %d of the merged training set:\n\n%s",
                    index, tokenizer.decode(train_sets[index]['input_ids'])
                )
            
    if data_args.resume_step is not None and data_args.resume_batch_size is not None:
        train_sets = train_sets[data_args.resume_step * data_args.resume_batch_size:]
        training_args.max_steps -= data_args.resume_step
        new_warmup_steps = max(0, training_args.warmup_steps - data_args.resume_step)
        new_learning_rate -= max(0, data_args.resume_step - training_args.warmup_steps) * (training_args.learning_rate / training_args.max_steps - training_args.warmup_steps)
        training_args.warmup_steps = new_warmup_steps
        training_args.learning_rate = new_learning_rate

    trainer = Trainer(
        args=training_args,
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_sets,
        callbacks=[LoggerCallback, RemoveStateCallback],
        data_collator=default_data_collator,
    )       

    trainer.train(resume_from_checkpoint=data_args.resume_from)
    
    trainer.save_model(training_args.output_dir)

if __name__ == "__main__":

    try:
        train()
    except Exception as e:
        logging.exception(e)
        exit(-1)
