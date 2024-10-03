import json
import os
from tqdm import tqdm
from io import StringIO
import sys


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


def load_jsonl(in_file):
    datas = []
    with open(in_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="load"):
            datas.append(json.loads(line))
    return datas


def save_jsonl(datas, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        for data in tqdm(datas, desc="save"):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def execute_code(code):
    codeOut = StringIO()
    codeErr = StringIO()
    sys.stdout = codeOut
    sys.stderr = codeErr
    exec(code)
    # restore stdout and stderr
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    error = codeErr.getvalue()
    output = codeOut.getvalue()
    return error, output
    
            
def to_blocks(text):
    computations = []
    if "**Computation" in text:
        blocks = ["**Computation" + e for e in text.split("**Computation")[1:]]
        for block in blocks:
            if "Conditions Needed:" in block and "Computation Expression:" in block and "Computation Result:" in block and "Python Code Snippet:" in block:
                orig_block = block
                title = block.split("Conditions Needed:")[0].strip("\n\t ")
                block = "\n".join([e.strip("\n\t ") for e in block.split("Conditions Needed:")[1:]])
                conditions = block.split("Computation Expression:")[0].strip("\n\t ")
                block = "\n".join([e.strip("\n\t ") for e in block.split("Computation Expression:")[1:]])
                expression = block.split("Computation Result:")[0].strip("\n\t ")
                block = "\n".join([e.strip("\n\t ") for e in block.split("Computation Result:")[1:]])
                result = block.split("Python Code Snippet:")[0].strip("\n\t ")
                block = "\n".join([e.strip("\n\t ") for e in block.split("Python Code Snippet:")[1:]])
                code = block[block.find("```python") + len("```python"):]
                code = code[:code.find("```")].strip("\n\t ")
                error, output = "", ""
                computations.append({"title": title, "conditions": conditions, "expression": expression, "result": result, "code": code, "execution_error": error, "execution_output": output})
    elif "Conditions Needed:" in text and "Computation Expression:" in text and "Computation Result:" in text and "Python Code Snippet:" in text:
        title = text.split("Conditions Needed:")[0].strip("\n\t ")
        text = "\n".join([e.strip("\n\t ") for e in text.split("Conditions Needed:")[1:]])
        conditions = text.split("Computation Expression:")[0].strip("\n\t ")
        text = "\n".join([e.strip("\n\t ") for e in text.split("Computation Expression:")[1:]])
        expression = text.split("Computation Result:")[0].strip("\n\t ")
        text = "\n".join([e.strip("\n\t ") for e in text.split("Computation Result:")[1:]])
        result = text.split("Python Code Snippet:")[0].strip("\n\t ")
        text = "\n".join([e.strip("\n\t ") for e in text.split("Python Code Snippet:")[1:]])
        code = text[text.find("```python") + len("```python"):]
        code = code[:code.find("```")].strip("\n\t ")
        error, output = "", ""
        computations.append({"title": "", "conditions": conditions, "expression": expression, "result": result, "code": code, "execution_error": error, "execution_output": output})
    return computations


def to_blocks_files(in_files, out_dir):
    for in_file in tqdm(in_files):
        out_file = os.path.join(out_dir, "to-blocks_" + os.path.basename(in_file))
        datas = load_jsonl(in_file)
        new_datas = []
        for data in tqdm(datas):
            computations = to_blocks(data["text"])
            new_datas.append({"idx": data["idx"], "model": data["model"], "computations": computations})
        save_jsonl(new_datas, out_file)


def main():
    in_dir = "data/mathematical_code_orig"
    in_files = [os.path.join(in_dir, file_name) for file_name in os.listdir(in_dir) if file_name.endswith("jsonl")]
    out_dir = "data/mathematical_code_blocks"
    to_blocks_files(in_files, out_dir)


if __name__ == "__main__":
    main()