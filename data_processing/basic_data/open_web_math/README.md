# Filtering of OpenWebMath

### Step 1: download data

Download [open-web-math/open-web-math](https://huggingface.co/datasets/open-web-math/open-web-math) and place it under `REPO_PATH/data` (REPO_PATH is the path to the repository). You can use `download.py` to do this.

### Step 2: start Server

Get the Docker from [text-generation-inference](https://github.com/huggingface/text-generation-inference), and run `deploy.sh` in the Docker environment to start the server hosting Mixtral-8x7B-Instruct.

### Step 3: start Annotation

To get paths to the files to be annotated, run:

```shell
python data_processing/basic_data/open_web_math/get_files.py
```

On the same machine as the server, run `process.sh`. Replace START_IDX and INTERVAL with the index and the number of process you are running. For example, if you started 4 processes on four different machines, then the INTERVAL is 4, and START_IDX is 0, 1, 2, 3 respectively.

```shell
bash data_processing/basic_data/open_web_math/process.sh START_IDX INTERVAL
```

Running this script results in annotation jsonl files saved under `REPO_PATH/data/open-web-math_Mixtral-8x7B-annotated`.

### Getting the Filtered Files

To get the filtered math-related files based on the annotation, run `get_math-related.py`. This file retains the documents in the original files that are annotated as math-related, and save the files containing the filtered documents under `data/open-web-math_filtered`
