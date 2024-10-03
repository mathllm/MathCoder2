import json
from argparse import ArgumentParser
import os
from glob import glob

def read_json(in_file):
    with open(in_file, "r", encoding="utf-8") as f:
        return json.load(f)

def compute_mmlu_math(data):
    subjects = ["mmlu_high_school_statistics", "mmlu_high_school_mathematics", "mmlu_elementary_mathematics", "mmlu_college_mathematics"]
    total_num = 0
    total_score = 0
    for subject in subjects:
        num = data["n-samples"][subject]["effective"]
        acc = data["results"][subject]["acc,none"]
        total_num += num
        total_score += num * acc
    avg_score = total_score / total_num
    
    return avg_score


def read_reault(in_dir, out_file):
    text = "|math|gsm8k|sat|ocw|mmlu-math|\n|"
    for i in range(5):
        text += "----|"
    text += "\n|"
    for dirname in ["math_mammoth", "gsm8k_mammoth"]:
        in_file = os.path.join(in_dir, dirname, "result_metrics.json")
        data = read_json(in_file)
        text += f"{data['acc']:.4f}|"
    for dirname in ["math_sat", "OCWCourses"]:
        in_file = os.path.join(in_dir, dirname, "metrics.json")
        data = read_json(in_file)
        text += f"{data['accuracy']:.4f}|"
    in_file = glob(os.path.join(in_dir, "lm_eval", "results*"))[0]
    data = read_json(in_file)
    acc = compute_mmlu_math(data)
    text += f"{acc:.4f}|"
    out_dir = os.path.dirname(out_file)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    print(text)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    parser = ArgumentParser()
    parser.add_argument("in_dir", type=str)
    
    args = parser.parse_args()
    in_dir = args.in_dir
    out_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results", os.path.basename(in_dir) + ".md")
    read_reault(in_dir, out_file)
    
if __name__ == "__main__":
    main()
