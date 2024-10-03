__conda_setup="$('/usr/local/lib/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/usr/local/lib/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/usr/local/lib/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/usr/local/lib/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup

conda activate deepseekenv

set -ex

dataset=$1
model_path=$2
out_dir=$3

CUDA_VISIBLE_DEVICES=0 TOKENIZERS_PARALLELISM=false python test/DeepSeek-Math/evaluation/infer/run_cot_eval.py \
--data_dir test/DeepSeek-Math/test_data/$dataset \
--save_dir $out_dir/$dataset \
--model_name_or_path $model_path \
--tokenizer_name_or_path $model_path \
--eval_batch_size 16 \
--temperature 0.0 \
--prompt_format few_shot \
--few_shot_prompt OCWCoursesPrompt \
--answer_extraction_fn extract_ocwcourses_few_shot_answer \
--eval_fn eval_ocwcourses  \
--use_vllm 