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

api = None

# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def save_jsonl(data: list, path: str, mode='w', verbose=True) -> None:
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
    global settings
    text = data["text"]
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
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "file_names.json"), "r") as f:
        file_names = json.load(f)
        
    ip = "127.0.0.1"
    api = API(ip=ip)
    
    for file_idx in range(start_idx, len(file_names), interval):
        data_file = file_names[file_idx]
        dataset = load_dataset("parquet", data_files=data_file, split="train")
        
        print("data_file:", data_file)
        print("number of texts:", len(dataset["text"]))
        
        # get path of out_file, make out_dir
        out_dir = settings["out_dir"]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_file = os.path.join(out_dir, "classified_" + os.path.basename(data_file)[:-8] + ".jsonl")
        
        settings_file = os.path.join(out_dir, "settings.json")
        with open(settings_file, "w") as f:
            json.dump(settings, f)
            
        if os.path.isfile(out_file):
            begin = len(load_jsonl(out_file))
        else:
            begin = 0
            
        # devide the text into blocks of at most 5000 characters
        texts_devided = []
        max_text_length = 5000
        for idx, text in enumerate(dataset["text"]):
            paragraphs = text.split("\n\n")
            text_devided = paragraphs[0]
            for paragraph in paragraphs[1:]:
                if len(text_devided) + len(paragraph) > 5000:
                    texts_devided.append({"idx": idx, "text": text_devided})
                    text_devided = paragraph
                else:
                    text_devided += "\n\n" + paragraph
            if len(text_devided) > 0:
                texts_devided.append({"idx": idx, "text": text_devided})
        del dataset

        end = len(texts_devided)
        outs = []
        counter = begin
        while counter < end:
            pool = Pool(16)
            try:
                results = pool.imap(process, texts_devided[begin:end])
                for d in tqdm(results, total=len(texts_devided[begin:end])):
                    outs.append(d)
                    counter += 1
                    if counter % 10 == 0 or counter == end:
                        if counter <= 10:
                            save_jsonl(outs, out_file, mode='w', verbose=False)
                        else:
                            save_jsonl(outs, out_file, mode='a', verbose=False)
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
    instruction = "You will be provided with a block of text. I need you to classify the text into one of the following types:\n1. The text describes a mathematical problem and its solution.\n2. The text explains a mathematical concept or mathematical theory.\n3. The text explains a scientific or engineering concept that requires mathematical knowledge.\n4. The text describes a programming problem and its solution.\n5. The text explains a concept or theory related to programming.\n6. The text explains the usage of a programming language or software tool.\n7. The text does not belong to any of the types above.\nHere's the text I've provided. Kindly analyze and classify it into type 1, 2, 3, 4, 5, 6 or 7. Put your choice behind 'The type is:'. Please do not generate any unrelated additional comments! The type number must match the type description. Here's one of the texts that needs to be classified: {text} The type is:"
    out_dir = "data/open-web-math_Mixtral-8x7B-annotated"
    
    settings = {
        "instruction": instruction,
        "out_dir": out_dir,
    }
    api = None
    
    main()
            
        
    
    
