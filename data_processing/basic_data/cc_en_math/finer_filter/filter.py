import fasttext
import os
import json
from tqdm import tqdm
from argparse import ArgumentParser


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../.."))


model = None

def save_jsonl(datas, out_file, mode="a"):
    with open(out_file, mode, encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
def main():
    parser = ArgumentParser()
    parser.add_argument("--start", type=int)
    parser.add_argument("--interval", type=int)
    args = parser.parse_args()
    print("start: ", args.start)
    print("interval: ", args.interval)
    global model
    model_path = "fasttext_models/model_related-vs-unrelated.bin"
    model = fasttext.load_model(model_path)
    thresh = 0.5
    in_dirs = [
        "data/cc-en-math_filtered"
    ]
    in_files = []
    for in_dir in in_dirs:
        in_files.extend([os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if file_name.startswith("simplified")])
    out_dir = "data/cc-en-math_filtered-finer_orig"
    for i in range(args.start, len(in_files), args.interval):
        in_file = in_files[i]
        print(in_file)
        out_file = os.path.join(out_dir, "filtered_" + os.path.basename(in_file))
        begin = 0
        if os.path.isfile(out_file):
            with open(out_file, "r", encoding="utf-8") as f:
                for line in f:
                    begin += 1
        with open(in_file, "r", encoding="utf-8") as f:
            out = []
            for idx, line in enumerate(f):
                print(f"{idx}\r", end="")
                if idx < begin:
                    continue
                orig_text = json.loads(line)["text"]
                text = orig_text.replace("\n", " ")
                predictions = model.predict([text,])[0]
                label = predictions[0][0]
                if label == "__label__related":
                    out.append({"i": idx, "t": "r", "text": orig_text})
                else:
                    out.append({"i": idx, "t": "u", "text": ""})
                if len(out) >= 10:
                    save_jsonl(out, out_file, mode="a")
                    out = []
            if len(out) > 0:
                save_jsonl(out, out_file, mode="a")
                out = []

    

if __name__ == "__main__":
    main()