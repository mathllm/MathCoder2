from datasets import load_dataset
import json
import os
from tqdm import tqdm


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in tqdm(datas, desc="save"):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def get_packages(code):
    lines = code.split("\n")
    packages = []
    for line in lines:
        if "import" in line:
            if "from" in line:
                packages.append(line.split("import")[0].replace("from", "").strip(" ").split(".")[0])
            else:
                packages.extend([e.strip(" ").split(".")[0] for e in line.split("as")[0].replace("import", "").strip(" ").split(",")])
    return packages


def filter_python_by_package(in_file, out_file):
    dataset = load_dataset("parquet", data_files=in_file, split="train")
    new_datas = []
    math_packages = ["sympy", "fractions", "cmath", "scipy", "statistics"]

    for max_stars_repo_path, max_stars_repo_name, max_stars_count, id, content in tqdm(zip(dataset["max_stars_repo_path"], dataset["max_stars_repo_name"], dataset["max_stars_count"], dataset["id"], dataset["content"])):
        extraced_imports = get_packages(content)
        packages = []
        for package in math_packages:
            if package in extraced_imports:
                packages.append(package)
        if len(packages) > 0:
            data = {
                "max_stars_repo_path": max_stars_repo_path,
                "max_stars_repo_name": max_stars_repo_name,
                "max_stars_count": max_stars_count,
                "id": id,
                "packages": ",".join(packages),
                "text": content
            }
            new_datas.append(data)

    save_jsonl(new_datas, out_file)


def main():
    in_dir = "data/starcoderdata/python"
    in_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir)]
    out_dir = "data/python_filtered"
    for in_file in tqdm(in_files):
        out_file = os.path.join(out_dir, "package-filtered_" + os.path.basename(in_file).split(".")[0] + ".jsonl")
        filter_python_by_package(in_file, out_file)


if __name__ == "__main__":
    main()

    