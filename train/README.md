# Continued Pretraining

This directory contains the code for continued pretraining.

## Installation

Create a conda environment:

```shell
conda create -n trainenv python=3.10
```

Activate the environment:

```shell
conda activate trainenv
```

Install torch from [PyTorch](https://pytorch.org/#:~:text=PyTorch%20is%20a%20Python-based,%20open%20source,%20and%20production-ready).

Install the required packages:

```shell
pip install -r train/requirements.txt
```

## Training

### Step 1: save the paths of the jsonl files to be tokenized

Modify `in_dirs` in `scripts/get_files_to-be-tokenized.py`. Exch element of `in_dirs` should be the path to a directory that contains `.jsonl` files with the texts to be trainined under the key `"text"`. Then run:

```shell
python train/scripts/get_files_to-be-tokenized.py
```

### Step 2: tokenize the files

You can modify `out_dir` in `scripts/tokenize_data.py` to change the output directory. Then run:

```shell
python train/scripts/tokenize_data.py
```

### Step 3: save the paths of the tokenized parquet files

You can modify `in_dirs` in `scripts/get_files_to-be-trained.py` to change the paths to the directories that contains the tokenized parquet files. Each element should be a path to a directory that contains parquet files created in Step 2. Then run:

```shell
python train/scripts/get_files_to-be-trained.py
```

### Step 4: group the texts into given context length

You can modify `max_len` in `scripts/group_text.py` to change the context length. This context length should equal the context length you wish to use in training. Then run:

```shell
python train/scripts/group_text.py
```

This outputs a single parquet file containing token indexes grouped into the given context length.

### Step 5: train the model

You can modify the training configs in `scripts/train.py`. The example script should be run on a cluster of 8 nodes with 4 A800 GPUs on each node. The cluster we used adpots an All Reduce-DDP structure, with `$WORLD_SIZE`, `$RANK` and `$MASTER_PORT` automatically configured. You may need to modify the script so that it runs on your cluster. Run:

```shell
bash train/scripts/train.sh
```

This script trains the model for 3 epochs with a batch size of 512 (8 node x 4 gpu_per_node x 4 per_device_train_batch_size x 4 gradient_accumulation_steps).