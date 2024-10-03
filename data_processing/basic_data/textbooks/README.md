# Processing Textbooks

We place the original pdf files under `data/textbooks_pdf`

### Step 1: get the paths to the pdf files

Run:

```shell
python data_processing/basic_data/textbooks/get_orig_pdf_paths.py
```

### Step 2: filter out duplicated or damaged pdf files

Run:

```shell
python data_processing/basic_data/textbooks/filter_pdf_and_get_text_fitz.py
```

This file remove the paths to the pdf files that are duplicated or damaged file.

### Step 3: create txt files with paths to pdfs

This step is in preparation of nougat convert. The file paths are devided into 30 .txt files so the conversion can be run in parallel.

Run:

```shell
python data_processing/basic_data/textbooks/write_file_paths_to_txt.py
```

### Step 4: nougat conversion

Run:

```shell
bash data_processing/basic_data/textbooks/convert_multi_files.sh $IDX
```

Relpace `$IDX` with index of the parallel process.

### Step 5: gather in converted mmd files into a jsonl file

Run:

```shell
bash data_processing/basic_data/textbooks/get_jsonl_from_mmd.py
```

This generates the final jsonl file at `data/textbooks_filtered/textbooks_nougat-converted_final.jsonl`.