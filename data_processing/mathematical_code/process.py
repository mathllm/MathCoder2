import re
import json
import os
import sys
from io import StringIO
import threading

from tqdm import tqdm
from multiprocessing import Pool,RLock
from huggingface_hub import InferenceClient
from datasets import load_dataset
from jupyter_client.manager import start_new_kernel
import zmq
import time
from argparse import ArgumentParser


# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))


api = None
in_file = None


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
    with open(path, "r", encoding='utf-8') as fh:
        return [json.loads(line) for line in fh.readlines() if line]


class API:

    def __init__(self, port='8001', ip='10.119.29.124'):
        self.client = InferenceClient(model=f'http://{ip}:{port}')

    def get_result(self, inputs, parameters=None):

        local_parameters = dict(max_new_tokens=3072, details=True, decoder_input_details=True)

        if parameters is not None:
            local_parameters.update(parameters)
        
        try:
            result = self.client.text_generation(prompt=inputs, **local_parameters)

            tokens_text = [token.text for token in result.details.tokens]
            text = "".join(tokens_text)

            return text
        except:
            import traceback
            traceback.print_exc()
            print(inputs) 
            return None


def process(data):
    global settings, in_file
    text = data["text"]
    instruction = settings["instruction"].format(text=text)
    system = settings["system"]
    
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    parameters=dict(
        do_sample=False,
        max_new_tokens=3072,
        stop_sequences=['<|eot_id|>'], 
        truncate=3072,
        details=True, 
        decoder_input_details=True
    )
    
    global api

    result = api.get_result(prompt, parameters)
    
    result = result.replace("<|eot_id|>", "").strip("\n\t ")
    
    if "idx" not in data.keys():
        data["idx"] = -1
    
    return {"idx": data["idx"], "text": result}


def main():
    global settings, api
    
    # parse argurments
    parser = ArgumentParser(description="A simple argument parser")
    parser.add_argument("--start_idx", type=int)
    parser.add_argument("--interval", type=int)
    args = parser.parse_args()
    
    start_idx = args.start_idx
    interval = args.interval
    
    # get file_names and ips
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "file_names.json"), "r") as f:
        file_names = json.load(f)

    ip = "127.0.0.1"
    api = API(ip=ip)
    
    global in_file
    
    for file_idx in range(start_idx, len(file_names), interval):
        in_file = file_names[file_idx]
        datas = load_jsonl(in_file)
        
        print("data_file:", in_file)
        
        print("number of texts:", len(datas))
        
        # get path of out_file, make out_dir
        out_dir = settings["out_dir"]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_file = os.path.join(out_dir, "computation-code_" + os.path.basename(in_file))
        
        settings_file = os.path.join(out_dir, "settings.json")
        with open(settings_file, "w") as f:
            json.dump(settings, f)
            
        if os.path.isfile(out_file):
            begin = len(load_jsonl(out_file))
        else:
            begin = 0
            
        end = len(datas)
        outs = []
        counter = begin
        while counter < end:
            pool = Pool(12)
            try:
                results = pool.imap(process, datas[begin:end])
                for d in tqdm(results, total=len(datas[begin:end])):
                    outs.append(d)
                    counter += 1
                    if counter % 10 == 0 or counter == end:
                        if counter <= 10:
                            save_jsonl(outs, out_file, mode='w', add_timestamp=False, verbose=False)
                        else:
                            save_jsonl(outs, out_file, mode='a', add_timestamp=False, verbose=False)
                        outs = []
                        begin = counter
            except Exception as e:
                print(e)
                print(f'<|{str(e)}|>')
                pool.terminate() 
                print(f"[restarting]")
                os.execl(sys.executable, sys.executable, *sys.argv)

            finally:
                pool.close()
                pool.join()
        
        print('Total: ', counter)

    
if __name__ == "__main__":
    system = "You are a clever mathematical AI assistant who is good at identifying complex comutations and solving them using python."
    instruction = "You will be presented with a text related to math. I need you to identify all the complex computations in it. For each complex computation that requires a scratchpad, find out the conditions needed for the computation, the latex expression that conducts the computation, and the result of the computation. Then generate a Python code snippet for each computation that demonstrates how the result is reached. Output each computation in the following format:\n\nConditions Needed:\n1. [Condition 1]\n2. [Condition 2]\n...\n\nComputation Expression:\n$[Latex Expression]$\n\nComputation Result:\n[Computation Result]\n\nPython Code Snippet:\n```python\n[Python Code]\n```\n\nThere can be more than one complex computation in the text. Output only the computations that requires calculation. Do not include mathematical statements or definitions as a computation. Make sure each snippet can be executed individually. The text is as follows: {text}\n\nThe computations are:"
    out_dir = "data/mathematical_code_orig"
    
    settings = {
        "instruction": instruction,
        "system": system,
        "out_dir": out_dir,
    }
    ape = None
    
    main()
            
        
    
    
