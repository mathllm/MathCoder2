#!/usr/bin/env python3

import re
import torch
import logging

logger = logging.getLogger()

IGNORE_INDEX = -100

class Processor:

    def group_texts(self, examples, tokenizer, max_len):
        input_ids, labels = [], []
        final_input_ids, final_labels = [], []
        
        for idx in range(len(examples['input_ids'])):
            _input_ids = examples['input_ids'][idx]
            _labels = examples['input_ids'][idx]
            examples['input_ids'][idx] = None
            if len(_input_ids) > max_len:
                # if single sample longer than max_len, break into several
                devided_input_ids, devided_labels = [], []
                for i in range(0, len(_input_ids), max_len):
                    devided_input_ids = _input_ids[i: i + max_len]
                    devided_labels =  _labels[i: i + max_len]
                    if len(devided_input_ids) < max_len:
                        devided_pad_num = max_len - len(devided_input_ids)
                        devided_input_ids += [tokenizer.pad_token_id] * devided_pad_num
                        devided_labels += [IGNORE_INDEX] * devided_pad_num
                    final_input_ids.append(devided_input_ids)
                    final_labels.append(devided_labels)
                continue
                    
            # if single sample shorter than max_len, combine together
            if len(input_ids) + len(_input_ids) > max_len:
                pad_num = max_len - len(input_ids)
                final_input_ids.append(input_ids + [tokenizer.pad_token_id] * pad_num)
                final_labels.append(labels + [IGNORE_INDEX] * pad_num)

                input_ids, labels = [], []
                
            input_ids.extend(_input_ids)
            labels.extend(_labels)
        
        if len(input_ids) > 0:
            pad_num = max_len - len(input_ids)
            final_input_ids.append(input_ids + [tokenizer.pad_token_id] * pad_num)
            final_labels.append(labels + [IGNORE_INDEX] * pad_num)

        return {
            "input_ids": torch.tensor(final_input_ids).long(),
            "labels": torch.tensor(final_labels).long()
        }
      
    def process_tokenize(self, exmaples, tokenizer):
        """
        tokenize samples and add bos and eos tokens
        """
        inputs = tokenizer(exmaples['text'], truncation=False, padding=False)

        input_ids, labels = [], []
        for input_id in inputs['input_ids']:
            if tokenizer.bos_token_id is not None:
                input_ids.append([tokenizer.bos_token_id] + input_id + [tokenizer.eos_token_id])
            else:
                input_ids.append(input_id + [tokenizer.eos_token_id])
        
        return {
            "input_ids": input_ids,
        }
