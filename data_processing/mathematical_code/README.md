# Generate Mathematical Code Accompanied with Reasoning Steps

### Step 1: get path to the files to be annotated

To get paths to the files to be annotated, run:

```shell
python data_processing/mathematical_code/get_files.py
```

This script creates `file_names.json`.

### Step 2: start server

Get the Docker from [text-generation-inference](https://github.com/huggingface/text-generation-inference), and run `deploy.sh` in the Docker environment to start the server hosting Mixtral-8x7B-Instruct. Run:

```shell
bash data_processing/mathematical_code/deploy.sh
```

### Step 3: start generating mathematical code

On the same machine as the server, run `process.sh`. Replace START_IDX and INTERVAL with the index and the number of process you are running. For example, if you started 4 processes on four different machines, then the INTERVAL is 4, and START_IDX is 0, 1, 2, 3 respectively.

```shell
bash data_processing/mathematical_code/process.sh START_IDX INTERVAL
```

Running this script results in annotation jsonl files saved under `data/mathematical_code_orig`.

### Step 4: extract the conditions, expressions, results, and code snippets

Run:

```shell
python data_processing/mathematical_code/extract_to_blocks.py
```

This generates extracted files under `data/mathematical_code_blocks`.

### Step 5: execute the code snippets

Run:

```shell
python data_processing/mathematical_code/execute_code.py
```

This results in files with execution results under `data/mathematical_code_blocks_executed`.

### Step 6: filter based on the result of execution

Run:

```shell
python data_processing/mathematical_code/execution_result_filter.py
```

This generates files under `data/mathematical_code_blocks_executed_filtered`

### Step 7: concatenate the reasoning step and code to form pretrain text

Run:

```shell
python data_processing/mathematical_code/convert_to_text.py
```

This generates the final files under `data/mathematical_code`