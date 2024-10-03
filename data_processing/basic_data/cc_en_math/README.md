# Filtering of CC-En

## Initial Filtering

### Step 1: Download CC-En files from Matrix

Run:

```shell
python data_processing/basic_data/cc_en_math/initial_filter/download.py
```

This script generates download the files under `data/cc-en`.

### Step 2: Generate training and testing files for fastText training

Run:

```shell
python data_processing/basic_data/cc_en_math/initial_filter/get_train_test_files.py
```

This script generates training file at `data/fasttext_filter-cc-en/math-vs-other_train.txt` and test file at `data/fasttext_filter-cc-en/math-vs-other_test.txt`.

### Step 3: Train the fastText model

Run:

```shell
bash data_processing/basic_data/cc_en_math/initial_filter/train.sh
```

for training. This script outputs a fastText model at `fasttext_models/model_math-vs-other.bin`. For testing, run:

```shell
bash data_processing/basic_data/cc_en_math/initial_filter/test.sh
```

### Step 4: filter with the fastText model generated in Step 3

Run:

```shell
bash data_processing/basic_data/cc_en_math/initial_filter/filter.sh
```

This scripts generates filtered files under the directory `data/cc-en-math_filtered_orig`

### Step 5: simplify the files in Step 4

The files in step 4 only set the irrelevant documents to an empty string. Run:

```shell
python data_processing/basic_data/cc_en_math/initial_filter/get_filtered_jsonl.py
```

to remove these empty entries to get the final filtered files under `data/cc-en-math_filtered`.

## Finer Filtering

The filtering in Initial Filtering is coarse, so we conduct a second round of Finer Filtering

### Step 2: start Server

Get the Docker from [text-generation-inference](https://github.com/huggingface/text-generation-inference), and run `deploy.sh` in the Docker environment to start the server hosting Mixtral-8x7B-Instruct.

### Step 3: start Annotation

On the same machine as the server, run `process.sh`. Replace START_IDX and INTERVAL with the index and the number of process you are running. For example, if you started 4 processes on four different machines, then the INTERVAL is 4, and START_IDX is 0, 1, 2, 3 respectively.

```shell
bash data_processing/basic_data/cc_en_math/finer_filter/process.sh START_IDX INTERVAL
```

Running this script results in annotation jsonl files saved under `data/cc-en-math_filtered_annotated`. You can stop the process when part of the data is annotated.

### Step 4: get train and test files for fastText

Run:

```shell
bash data_processing/basic_data/cc_en_math/finer_filter/filter.sh
```

This script generates filtered files under `data/cc-en-math_filtered-finer_orig`.

### Step 5: remove the unrelated documents from the filtered files

Run:

```shell
python data_processing/basic_data/cc_en_math/finer_filter/get_filtered_jsonl.py
```

This generates files under `data/cc-en-math_filtered-finer`.