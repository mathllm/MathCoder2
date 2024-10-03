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

conda activate lm-eval

task_names="mmlu"
model_path=${1}
out_dir=${2}

lm_eval --model hf \
    --model_args pretrained=$model_path \
    --tasks $task_names \
    --device cuda:0 \
    --batch_size 8 \
    --output_path ${out_dir}/lm_eval/ \
    --log_samples