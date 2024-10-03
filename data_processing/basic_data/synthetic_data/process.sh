start_idx=${1}
interval=${2}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd /

conda init bash
apt-get update
apt-get install tmux -y
source ~/.bashrc

source /opt/conda/etc/profile.d/conda.sh
conda activate dataenv

tmux new-session -d -s education_$start_idx "python $DIR/process.py --start_idx $start_idx --interval $interval"
sleep 1s
tmux ls