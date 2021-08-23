import os
import copy
import random
import argparse
import numpy as np
from time import time
import torch
import bert_codes.tokenization as tokenization
import bert_codes.utils as utils
import ipdb


# Configuration
##############################################################################################
t_config = time()
parser = argparse.ArgumentParser()
parser.add_argument('--gpu_ids', type=str, default='1, 2, 3, 4')
# training parameter
parser.add_argument('--max_query_length', type=int, default=64)  # former sentence
parser.add_argument('--max_ans_length', type=int, default=64)  # later sentencee
parser.add_argument('--float16', type=bool, default=True)  # only sm >= 7.0 (tensorcores)
parser.add_argument('--seed', type=int, default=215)
parser.add_argument('--vocab_size', type=int, default=21128)  # number of vocabularies in vocab.txt
# data and model dir
parser.add_argument('--checkpoint_dir', type=str, default='check_points/islandtalker_model')
args = parser.parse_args()
    
# set seed
random.seed(args.seed)
np.random.seed(args.seed)
torch.manual_seed(args.seed)   
 
# set gpu
os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_ids
device = torch.device("cuda")
n_gpu = torch.cuda.device_count()
if n_gpu > 0:
    torch.cuda.manual_seed_all(args.seed)
    
# set tokenizer
tokenizer = tokenization.BertTokenizer(vocab_file='./pretrained_model/unilm_1.2/vocab.txt', do_lower_case=True)

# set model
model = torch.load(args.checkpoint_dir + '/best_model.pth')
model.to(device)
if args.float16:
    model.half()
if n_gpu > 1:
    model = torch.nn.DataParallel(model)
print("Configuration Time: {}".format(time() - t_config))


# Data Preprocessing
##############################################################################################
def prepro(s):
    lst_token = list()  
    for c in utils.split_sent(s):
        lst_token.extend(tokenizer.tokenize(c))
    if len(lst_token) == 0:
        return None
    # cut and catenate      
    input_tokens = None
    while len(lst_token) + 2 > args.max_query_length:  # [CLS] + [SEP]
        lst_token = lst_token[:-1]
    if len(lst_token) > 0:
        input_tokens = ["[CLS]"] + lst_token + ["[SEP]"]
    else:
        return None
    # token to ids
    input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
    input_mask = [1] * len(input_tokens)
    output_idx = [len(input_tokens)]
    segment_ids = [0] * len(input_tokens)
    context_mask = [1] * len(input_tokens)
    # padding
    while len(input_ids) < args.max_query_length + args.max_ans_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)
        context_mask.append(0)
    if len(input_ids) == len(input_mask) == len(segment_ids) == len(context_mask):
        f = { "input_ids": input_ids, 
            "input_mask": input_mask, 
            "segment_ids": segment_ids,
            "context_mask": context_mask, 
            "output_idx": output_idx,
            "pred_ids":[]}
        return f
    else:
        return None


# Evaluate
##############################################################################################
def evaluate(d, END_id=99):
    global model, device
    '''
    :param model: model
    :param device: 数据转移到gpu
    :param END_id: 结束终结符，这里使用默认的[END]token
    '''
    with torch.no_grad():
        while True:
            input_ids = torch.tensor([d['input_ids']], dtype=torch.long).to(device=device)
            input_mask = torch.tensor([d['input_mask']], dtype=torch.long).to(device=device)
            context_mask = torch.tensor([d['context_mask']], dtype=torch.long).to(device=device)
            segment_ids = torch.tensor([d['segment_ids']], dtype=torch.long).to(device=device)
            output_idx = torch.tensor([d['output_idx']], dtype=torch.long).to(device=device)
            pred = model( input_ids=input_ids,
                      token_type_ids=segment_ids, 
                      attention_mask=input_mask, 
                      context_mask=context_mask,
                      output_idx = output_idx, 
                      is_train=False)
            pred = pred.cpu().numpy()
            pred = np.argmax(pred, axis=1)
            # 新生成的字更新给d，再带入与测下一个字，target是偏移序号
            target = d["output_idx"][0] + 1 
            d["pred_ids"].append(pred[0])
            if (target < args.max_query_length + args.max_ans_length) and pred != END_id:# 未到长度上限，且非[END], 继续生成
                d["input_ids"][target] = pred
                d["input_mask"][target] = 1
                d["segment_ids"][target] = 1
                d["output_idx"] = [target]
            else:
                break
    # id2token
    pred_tokens = tokenizer.convert_ids_to_tokens(d["pred_ids"])
    pred_text = []
    for token in pred_tokens:
        if token == "[END]":
            break
        pred_text.append(token)
    pred_text = utils.combine_tokens(pred_text)
    pred_text = " ".join(pred_text.split()) 
    return pred_text


# Predict
##############################################################################################
def predict(s):
    d = prepro(s)
    if d is None:
        return "Wrong input ..."
    res = evaluate(d)
    if len(res) == 0:
        return "There is no response ..."
    return res


# Main
##############################################################################################
if __name__ == '__main__':
    s = "阿米娅对于感染者的看法"
    print("问：{}\n答：{}".format(s, predict(s)))
     
