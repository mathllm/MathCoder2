# Filtering of Code Using Math Packages

### Step 1: Download files from starcoderdata

Run:

```shell
python data_processing/basic_data/code_with_math_packages/download.py
```

This script download the files under `data/starcoderdata`.

### Step 2: Filter the files by detecting package import

Run:

```shell
python data_processing/basic_data/code_with_math_packages/filter_jupyter-script.py
python data_processing/basic_data/code_with_math_packages/filter_jupyter-structured.py
python data_processing/basic_data/code_with_math_packages/filter_python.py
```

The three python scripts generates filtered files under `data/jupyter-script_filtered`, `data/jupyter-structured_filtered` and `data/python_filtered` respectively.