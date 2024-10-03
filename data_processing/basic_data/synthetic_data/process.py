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
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


api = None


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

def get_number(text):
    numbers = re.findall(r'\d', text)
    if len(numbers) == 0:
        return None
    else:
        return numbers[0]
    
def process_text(text):
    first_line = text.split("\n")[0]
    if "revised" in first_line:
        text = text[len(first_line):].strip("\n\t ")
    return text

def process(data):
    global settings
    text = data["text"]
    text = process_text(text)
    instruction = settings["instruction"].format(text=text)
    
    prompt = f"<s> [INST] {instruction} [/INST]"
    parameters=dict(
        do_sample=False,
        max_new_tokens=3072,
        stop_sequences=["</s>", "\n\n", "."], 
        truncate=3072,
        details=True, 
        decoder_input_details=True
    )
    
    global api
    
    result = api.get_result(prompt, parameters)
    
    result = result.replace("</s>", "").strip("\n\t ")
    
    type_number = get_number(result)
    
    return {"idx": data["idx"], "type_number": type_number, "text": text}

def main():
    global settings, api
    
    # parse argurments
    parser = ArgumentParser(description="A simple argument parser")
    parser.add_argument("--start_idx", type=int)
    parser.add_argument("--interval", type=int)
    args = parser.parse_args()
    
    start_idx = args.start_idx
    interval = args.interval
    
    # get file_names
    in_dir = "data/Education-College-Students_filtered-by-rule"
    file_names = [os.path.join(in_dir, file) for file in os.listdir(in_dir)]

    ip = "127.0.0.1"
    api = API(ip=ip)
    
    for file_idx in range(start_idx, len(file_names), interval):
        data_file = file_names[file_idx]
        dataset = load_dataset("json", data_files=data_file, split="train")
        
        print("data_file:", data_file)
        
        print("number of texts:", len(dataset["text"]))
        
        # get path of out_file, make out_dir
        out_dir = settings["out_dir"]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_file = os.path.join(out_dir, "classified_" + os.path.basename(data_file))
        
        settings_file = os.path.join(out_dir, "settings.json")
        with open(settings_file, "w") as f:
            json.dump(settings, f)
            
        if os.path.isfile(out_file):
            begin = len(load_jsonl(out_file))
        else:
            begin = 0
            
        datas = []
        for idx, text, model in zip(dataset["idx"], dataset["text"], dataset["model"]):
            datas.append({"idx": idx, "text": text, "model": model})

        end = len(datas)
        outs = []
        counter = begin
        while counter < end:
            pool = Pool(64)
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
    instruction = "You will be provided with a block of text. I need you to classify the text into one of the following types:\n1. The text is related to math.\n2. The text is not related to math.\nHere's the text I've provided. Kindly analyze and classify it into type 1 or 2. Put your choice behind 'The type is:'. Please do not generate any unrelated additional comments! The type number must match the type description. Here's one of the texts that needs to be classified: {text} The type is:"
    out_dir = "data/Education-College-Students_filtered-by-rule_filtered-by-model"
    
    settings = {
        "instruction": instruction,
        "out_dir": out_dir,
    }
    ape = None
    
    main()
            
        
    
    
