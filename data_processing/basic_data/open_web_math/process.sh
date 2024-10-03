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

# deploy the model
tmux new-session -d -s deploy "bash $DIR/deploy.sh"

conda activate dataenv

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

start_idx=$1
interval=$2

sleep 10s
# start inference client
tmux new-session -d -s $start_idx "python $DIR/process.py --start_idx $start_idx --interval $interval"
sleep 10s
tmux ls