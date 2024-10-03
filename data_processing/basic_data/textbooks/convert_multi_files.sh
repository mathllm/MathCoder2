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

export NCCL_DEBUG=WARN
export NCCL_SOCKET_IFNAME=eth0

export NCCL_IB_TIMEOUT=22   
export NCCL_IB_RETRY_CNT=13 
export NCCL_IB_AR_THRESHOLD=0

conda activate dataenv

IDX=$1
PATH_FILE=data/textbooks_nougat_convert/file_paths/$IDX.txt

nougat $PATH_FILE \
-o data/textbooks_nougat_convert/converted/$IDX \
--checkpoint models/nougat-0.1.0-base \
--batchsize 16
