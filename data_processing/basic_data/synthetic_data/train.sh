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

conda activate dataenv

./fasttext supervised \
-input data/fasttext_filter-matrix-math-science/open-web-math-vs-matrix-math-science_train.txt \
-output fasttext_models/model_open-web-math-vs-matrix-math-science \
-lr 0.5 \
-epoch 5 \
-wordNgrams 2 \
-bucket 200000 \
-dim 50 \
-loss one-vs-all

