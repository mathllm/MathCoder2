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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

conda activate trainenv

export NCCL_DEBUG=WARN
export NCCL_SOCKET_IFNAME=eth0

export NCCL_IB_TIMEOUT=22   
export NCCL_IB_RETRY_CNT=13 
export NCCL_IB_AR_THRESHOLD=0

wandb login $WANDB_TOKEN

OMP_NUM_THREADS=1 torchrun --nnodes $WORLD_SIZE --node_rank $RANK --master_addr $MASTER_ADDR --master_port $MASTER_PORT --nproc_per_node 4 train/train.py \
--ddp_timeout 360000 \
--model_cfg meta-llama/Meta-Llama-3-8B \
--train_parquet_file data/tokenized_Meta-Llama-3-8B/grouped.parquet \
--output_dir outs/MathCoder2-Llama-3-8B \
--dataloader_num_workers 32 \
--max_len 8192 \
--max_steps -1 \
--num_train_epochs 3 \
--save_steps 500 \
--warmup_steps 50 \
--logging_steps 10 \
--learning_rate 4e-5 \
--weight_decay 0.1 \
--lr_scheduler_type cosine \
--per_device_train_batch_size 4 \
--gradient_accumulation_steps 4 \
--seed 3407 \
--deepspeed train/config/deepspeed.json \
--bf16 \
--stream \
--do_train \
--overwrite_output_dir \
--gradient_checkpointing \
--report_to wandb \
--run_name MathCoder2-Llama-3-8B \
--save_total_limit 20 \