# Data Decontamination

We use exact match to remove the identical samples and further apply 13-gram deduplication (with a condition that the Jaccard similarity should be larger than 0.6) to remove more samples that might cause contamination.

### Step 1: get paths to the files you wish to decontaminate

run:

```shell
python data_processing/decontamination/get_files.py
```

This script creates a `file_names.json` under the `data_processing/decontamination` directory containing a list of paths to the files you wish to decontaminate.

### Step 2: run the decontamination

run:

```shell
python data_processing/decontamination/exact_match_and_13-gram.py
```

This creates a directory `data/MathCode-Pile_decontaminated` containing the decontaminated files, and another directory `data/MathCode-Pile_contaminated` containining documents that are contaminated. Running this script showns that very few documents are contaminated.