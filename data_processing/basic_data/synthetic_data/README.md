# Filter Existing Synthetic Data from Open-source Repositories

## Download the original files

Run:

```shell
python data_processing/basic_data/synthetic_data/download.py
```

This script generates download the files under `data/Maths-College`, `data/Education-College-Students`, and `data/Matrix_math_science`.

## Process Education-College-Students and Maths-College

### Step 1: Filter Education-College-Students by rule

Run:

```shell
python data_processing/basic_data/synthetic_data/get_filtered_math-related_by-rule.py
```

This detect mathematical expressions in the texts and remove those with no mathematical expressions.

### Step 2: Filter Education-College-Students with Mixtral-8x7B-Instruct

Get the Docker from [text-generation-inference](https://github.com/huggingface/text-generation-inference), and run `deploy.sh` in the Docker environment to start the server hosting Mixtral-8x7B-Instruct.

Run:

```shell
bash data_processing/basic_data/synthetic_data/process.sh
```

This file generates annotated files under `data/Education-College-Students_filtered-by-rule_filtered-by-model`.

### Step 3: remove the irrelevant documents in Step 2

Run:

```shell
python  data_processing/basic_data/synthetic_data/get_filtered_math-related.py
```

This generates filtered files under the directory `data/synthetic_filtered`.

### Step 4: Move Maths-College files to data/synthetic_filtered

We observe that texts in Maths-College are mostly highly related to math, so we directly move the Maths-College files to data/synthetic_filtered:

```shell
mv data/Maths-College/* data/synthetic_filtered
```

## Process Matrix_math_science

### Step 1: sample training and test data for fastText classifier

Run:

```shell
python data_processing/basic_data/synthetic_data/get_train_test_files.py
```

### Step 2: train fastText classifer

Run:

```shell
bash data_processing/basic_data/synthetic_data/train.sh
```

### Step 3: filter the files

Run:

```shell
bash data_processing/basic_data/synthetic_data/filter.sh
```

### Step 4: get the final filtered files in data/synthetic_filtered

Run:

```shell
python data_processing/basic_data/synthetic_data/get_filtered_jsonl.py
```
