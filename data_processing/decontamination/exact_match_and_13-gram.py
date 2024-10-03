import os
import json
from tqdm import tqdm
from argparse import ArgumentParser
from datasets import load_dataset
import sys

from multiprocessing import Pool,RLock
import time
import difflib
import nltk


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


model = None
test_samples = []

def timestamp() -> str:
    nowtime = time.strftime('-%Y%m%d-%H%M', time.localtime(time.time()))
    print(nowtime)  
    return nowtime  


def save_jsonl(data: list, path: str, mode='w', add_timestamp=True, verbose=True) -> None:
    if add_timestamp:
        file_name = f"{path.replace('.jsonl','')}{timestamp()}.jsonl"
    else:
        file_name = path
    with open(file_name, mode, encoding='utf-8') as f:
        if verbose:
            for line in tqdm(data, desc='save'):
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        else:
            for line in data:
                f.write(json.dumps(line, ensure_ascii=False) + '\n')


def load_jsonl(path: str):
    datas = []
    with open(path, "r", encoding='utf-8') as f:
        for line in tqdm(f, desc="load"):
            datas.append(json.loads(line))
    return datas


def is_duplicate(text, ngram_size=13, threshold=0.6):
    global test_samples
    # Generate n-grams
    ngrams1 = set(nltk.ngrams(text.split(), ngram_size))

    for text2 in test_samples:
        if text in text2:
            return {"text": text, "duplicate": text2}
        ngrams2 = set(nltk.ngrams(text2.split(), ngram_size))

        # Find intersection and union
        intersection = ngrams1.intersection(ngrams2)
        union = ngrams1.union(ngrams2)
        
        if len(union) == 0:
            return {"text": text}
        # Calculate Jaccard similarity
        similarity = len(intersection) / len(union)

        if similarity > threshold:
            return {"text": text, "duplicate": text2}
    return {"text": text}


def main():
    global test_samples
    parser = ArgumentParser()
    parser.add_argument("--start", type=int)
    parser.add_argument("--interval", type=int)
    args = parser.parse_args()
    print("start: ", args.start)
    print("interval: ", args.interval)

    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "file_names.json")
    with open(config_file, "r", encoding="utf-8") as f:
        in_files = json.load(f)

    test_config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_files.json")
    with open(test_config_file, "r", encoding="utf-8") as f:
        test_files = json.load(f)
    for file in test_files:
        test_samples.extend([data["question"] for data in load_jsonl(file)])
    print("test_samples: ", len(test_samples))

    out_dir = "data/MathCode-Pile_decontaminated"
    out_dir_duplicate = "data/MathCode-Pile_contaminated"
    for i in range(args.start, len(in_files), args.interval):
        in_file = in_files[i]
        print("in_file: ", in_file)

        out_file = os.path.join(out_dir, os.path.basename(os.path.dirname(in_file)), "decontaminated_" + os.path.basename(in_file))
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        print("out_file: ", out_file)

        out_file_duplicate = os.path.join(out_dir_duplicate, os.path.basename(os.path.dirname(in_file)), "contaminated_" + os.path.basename(in_file))
        if not os.path.exists(os.path.dirname(out_file_duplicate)):
            os.makedirs(os.path.dirname(out_file_duplicate))
        print("out_file_duplicate: ", out_file_duplicate)
        begin = 0
        if os.path.isfile(out_file):
            continue
        texts = load_dataset("json", data_files=in_file, split="train")["output"]

        end = len(texts)
        outs = []
        outs_duplicate = []
        counter = begin
        pool = Pool(20)
        try:
            results = pool.imap(is_duplicate, texts[begin:end])
            for d in tqdm(zip(results, texts[begin:end]), total=len(texts[begin:end])):
                if "duplicate" in d[0].keys():
                    outs_duplicate.append(d[0])
                else:
                    outs.append(d)

            save_jsonl(outs, out_file, mode='w', add_timestamp=False, verbose=False)
            save_jsonl(outs_duplicate, out_file_duplicate, mode='w', add_timestamp=False, verbose=False)
        except Exception as e:
            print(e)
            print(f'<|{str(e)}|>')
            pool.terminate()
            print(f"[restarting]")
            os.execl(sys.executable, sys.executable, *sys.argv)

        finally:
            pool.close()
            pool.join()


if __name__ == "__main__":
    main()
