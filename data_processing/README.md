# Data Processing

## Installation

Create a conda environment:

```shell
conda create -n dataenv python=3.10
```

Activate the environment:

```shell
conda activate dataenv
```

Install required packages:

```shell
pip install -r data_processing/requirements.txt
```

Install fastText:

```shell
$ git clone https://github.com/facebookresearch/fastText.git
$ cd fastText
$ mkdir build && cd build && cmake ..
$ make && make install
```

Install nougat:

```shell
pip install git+https://github.com/facebookresearch/nougat
```

## Documentations

The documentations for generating each part of the MathCode-Pile dataset are as follows:

- [filtered-OpenWebMath](data_processing/basic_data/open_web_math/README.md)
- [filtered-CC-En-math](data_processing/basic_data/cc_en_math/README.md)
- [synthetic data](data_processing/basic_data/synthetic_data/README.md)
- [code using math packages](data_processing/basic_data/code_with_math_packages/README.md)
- [mathematical textbooks](data_processing/basic_data/textbooks/README.md)
- [translated mathematical code](data_processing/mathematical_code/README.md)

The documentation for decontamination is at: [decontamination](data_processing/decontamination/README.md).