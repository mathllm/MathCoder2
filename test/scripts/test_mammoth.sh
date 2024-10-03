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

conda activate mammoth

cd /mnt/cache/luzimu/math_pretrain/evaluation/MAmmoTH/math_eval

dataset=${1}
model_path=${2}
out_dir=${3}

python run_open.py \
  --model $model_path \
  --shots 4 \
  --dataset $dataset \
  --form short \
  --output ${out_dir}/${dataset}_mammoth/result.jsonl