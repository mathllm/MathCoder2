model_path=${1}
out_dir=${2}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

declare -a arr=("OCWCourses"
                "math_sat")

for dataset in "${arr[@]}"
do
   bash test/DeepSeek-Math/evaluation/scripts/infer_deepseek-pretrain_$dataset.sh $dataset $model_path $out_dir
done
