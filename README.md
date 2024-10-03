# MathCoder2

This repository contains files for data processing and continued pretraining to reproduce the paper "MathCoder2: Better Math Reasoning from Continued Pretraining on Model-translated Mathematical Code".

## Data Processing

The documentations for generating each part of the MathCode-Pile dataset are as follows:

- [filtered-OpenWebMath](data_processing/basic_data/open_web_math/README.md)
- [filtered-CC-En-math](data_processing/basic_data/cc_en_math/README.md)
- [synthetic data](data_processing/basic_data/synthetic_data/README.md)
- [code using math packages](data_processing/basic_data/code_with_math_packages/README.md)
- [mathematical textbooks](data_processing/basic_data/textbooks/README.md)
- [translated mathematical code](data_processing/mathematical_code/README.md)

The documentation for decontamination is at: [decontamination](data_processing/decontamination/README.md).

## Training

The documentation for training is at: [training](train/README.md)

## Testing

The documentation for testing is at: [evaluation](test/README.md).

