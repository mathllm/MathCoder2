# Testing

## Installation

Install conda environments `deepseekenv`, `mammoth` and `lm-eval` based on instructions in [DeepSeek-Math](https://github.com/deepseek-ai/DeepSeek-Math/blob/main/evaluation/README.md), [MAmmoTH](https://github.com/TIGER-AI-Lab/MAmmoTH/blob/main/README.md), and [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/README.md)

## Evaluation

To evaluate the models, run `scripts/eval.sh`:

```shell
bash test/scripts/eval.sh $MODEL_PATH $OUTPUT_DIR
```

Replace `$MODEL_PATH` with the path to the directory where the model weights are stored, and replace `$OUTPUT_DIR` with the path to the directory where you wish the inference results would be saved. This script would also create a `result` directory under `test/scripts` where markdown files containing a table of all the results would be saved.