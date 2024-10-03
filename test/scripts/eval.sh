model_path=${1}
out_dir=${2}

TOKENIZERS_PARALLELISM=true

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

bash $DIR/test_mammoth.sh gsm8k $model_path $out_dir

bash $DIR/test_mammoth.sh math $model_path $out_dir

bash $DIR/test_multi_tasks.sh $model_path $out_dir

bash $DIR/test_deepseekmath.sh $model_path $out_dir

python $DIR/read_result.py $out_dir