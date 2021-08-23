import os
import re
import copy
import json
import random
import argparse
import numpy as np
from time import time
from tqdm import tqdm
import torch
from torch.utils.data import TensorDataset, DataLoader
from bert_codes.modeling import Seq2SeqModel, BertConfig
from bert_codes.optimization import AdamW, get_linear_schedule_with_warmup
import bert_codes.tokenization as tokenization
import bert_codes.utils as utils
import ipdb

# Configuration
##############################################################################################
t_config = time()
parser = argparse.ArgumentParser()
parser.add_argument('--gpu_ids', type=str, default='1, 2, 3, 4')  # gpu id
# training parameter
parser.add_argument('--train_epochs', type=int, default=50)
parser.add_argument('--batch_size', type=int, default=64)
parser.add_argument('--eval_batch_size', type=int, default=128)
parser.add_argument('--max_a_length', type=int, default=32)  # former sentence
parser.add_argument('--max_b_length', type=int, default=32)  # later sentencee
parser.add_argument('--max_lines', type=str, default=-1)  # number of lines readed from the raw text
parser.add_argument('--balance', type=int, default=0.4)
parser.add_argument('--lr', type=float, default=1e-5)
parser.add_argument('--dropout', type=float, default=0.1)
parser.add_argument('--clip_norm', type=float, default=1.0)
parser.add_argument('--warmup_rate', type=float, default=0.1)
parser.add_argument("--schedule", default='warmup_linear', type=str, help='schedule')
parser.add_argument("--weight_decay_rate", default=0.01, type=float, help='weight_decay_rate')
parser.add_argument('--float16', type=bool, default=True)  # only sm >= 7.0 (tensorcores)
parser.add_argument('--seed', type=int, default=215)
parser.add_argument('--log_interval', type=int, default=50)
parser.add_argument('--vocab_size', type=int, default=21128) # number of vocabularies in vocab.txt
# data and model dir
parser.add_argument('--train_dir', type=str, default='./data/story_train.json')
parser.add_argument('--dev_dir', type=str, default='./data/story_dev.json')
parser.add_argument('--feature_train_dir', type=str, default='./data/fea_story_train.json')
parser.add_argument('--feature_dev_dir', type=str, default='./data/fea_story_dev.json')
parser.add_argument('--bert_config_file', type=str, default='./pretrained_model/unilm_1.2/config.json')  # open-source unilm config file
parser.add_argument('--init_restore_dir', type=str, default='./pretrained_model/unilm_1.2/unilm.pth')  # open-source unilm model
parser.add_argument('--checkpoint_dir', type=str, default='check_points/islandtalker_model')  # your newly generated model
parser.add_argument('--setting_file', type=str, default='setting.txt')
parser.add_argument('--log_file', type=str, default='log.txt')
parser.add_argument('--log_result_file', type=str, default='log_result_now_epoch.txt')
# set args
args = parser.parse_args()
utils.check_args(args)
    
# bert initialization
bert_config = BertConfig.from_json_file(args.bert_config_file)
bert_config.attention_probs_dropout_prob = args.dropout
bert_config.hidden_dropout_prob = args.dropout
tokenizer = tokenization.BertTokenizer(vocab_file='./pretrained_model/unilm_1.2/vocab.txt', do_lower_case=True)
model = Seq2SeqModel(bert_config)

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
print("device %s n_gpu %d" % (device, n_gpu))
print("device: {} n_gpu: {} 16-bits training: {}".format(device, n_gpu, args.float16))

# set model
print('***** Initializing Model *****')
utils.torch_init_model(model, args.init_restore_dir)
model.to(device)
    
# set log
if os.path.exists(args.log_file):
    os.remove(args.log_file)

print("Configuration Time: {}".format(time() - t_config))


# Data Preprocessing
##############################################################################################
def data2fea(load_path, save_path, learn_tag="train"):
    global args
    if os.path.exists(save_path):
        print("***** Loading Data *****")
        with open(save_path, "r") as f:
            features = json.load(f)
    else:
        print("***** Creating Data *****")
        with open(load_path, "r") as f:
            lst_sentence = json.load(f)
         # 构建[CLS]上一句[SEP]下一句[END]
        features = list()
        i_sample = 0
        d_unk = dict()  # to store oov
        for i_sent in tqdm(range(len(lst_sentence)-1)):
            if args.max_lines > 0:
                if i_sample > args.max_lines:
                    break
            text_a, text_b = lst_sentence[i_sent].strip(), lst_sentence[i_sent + 1].strip()
            token_a = list()  
            for wa in utils.split_sent(text_a):
                t = tokenizer.tokenize(wa)
                if "[UNK]" in t:
                    if wa in d_unk.keys():
                        d_unk[wa] += 1
                    else:
                        d_unk[wa] = 1
                token_a.extend(t)
            token_b = list()  
            for wb in utils.split_sent(text_b):
                t = tokenizer.tokenize(wb)
                if "[UNK]" in t:
                    if wb in d_unk.keys():
                        d_unk[wb] += 1
                    else:
                        d_unk[wb] = 1
                token_b.extend(t)
            if len(token_a) == 0 or len(token_b) == 0:
                continue
            # cut and catenate      
            input_tokens = None
            if learn_tag == "train":
                while len(token_a) + 2 > args.max_a_length:
                    token_a = token_a[:-1]
                while len(token_b) + 1 > args.max_b_length:
                    token_b = token_b[:-1]
                if len(token_a) > 0 and len(token_b) > 0:
                    input_tokens = ["[CLS]"] + token_a + ["[SEP]"] + token_b + ["[END]"]                  
            else:
                while len(token_a) + 2 > args.max_a_length:  # [CLS] + [SEP]
                    token_a = token_a[:-1]
                if len(token_a) > 0:
                    input_tokens = ["[CLS]"] + token_a + ["[SEP]"]
            if input_tokens is None:
                    continue
            # token to ids
            input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
            input_mask = [1] * len(input_tokens)
            output_idx = [len(token_a) + 2]
            if learn_tag == "train":
                segment_ids = [0] * (len(token_a) + 2) + [1] * (len(token_b) + 1)
                context_mask = [1] * (len(token_a) + 2) + [0] * (len(token_b) + 1)     
            else:
                segment_ids = [0] * (len(token_a) + 2)
                context_mask = [1] * (len(token_a) + 2)
            # padding
            while len(input_ids) < args.max_a_length + args.max_b_length:
                input_ids.append(0)
                input_mask.append(0)
                segment_ids.append(0)
                context_mask.append(0)
            assert len(input_ids) == len(input_mask) == len(segment_ids) == len(context_mask)
            # get true text
            true_text = utils.combine_tokens(token_b)
            true_text = " ".join(true_text.split())
            # insert to the learning data
            f_now = {"idx": i_sample,
                  "input_ids": input_ids, 
                  "input_mask": input_mask,
                  "segment_ids": segment_ids, 
                  "context_mask": context_mask,
                  "output_idx": output_idx, 
                  "true_text": true_text}
            if learn_tag == "dev" or learn_tag == "test":
                f_now["batch_idx"] = i_sample % args.eval_batch_size
                f_now["pred_ids"] = []
            i_sample += 1
            features.append(f_now)
        # save
        with open(save_path, "w") as f:
            json.dump(features, f)
        print(d_unk)  # 打印未知单词
    return features
  
    
def prepare_for_train():
    global args
    # get features
    train_features = data2fea(load_path=args.train_dir, save_path=args.feature_train_dir, learn_tag="train")
    dev_features = data2fea(load_path=args.dev_dir, save_path=args.feature_dev_dir, learn_tag="dev")     
    # get train dataloader
    train_input_ids = torch.tensor([f['input_ids'] for f in train_features], dtype=torch.long)
    train_input_mask = torch.tensor([f['input_mask'] for f in train_features], dtype=torch.long)
    train_segment_ids = torch.tensor([f['segment_ids'] for f in train_features], dtype=torch.long)
    train_context_mask = torch.tensor([f['context_mask'] for f in train_features], dtype=torch.long)
    train_tensor = TensorDataset(train_input_ids, train_input_mask, train_segment_ids, train_context_mask)
    train_dataloader = DataLoader(train_tensor, batch_size=args.batch_size, shuffle=True)
    print("Train-{}, Dev-{}".format(len(train_features), len(dev_features)))
    return train_features, train_dataloader, dev_features


# Evaluate
##############################################################################################
def get_score(y_true, y_pred, mode="f1"):
    # both y_true and y_pred are strings
    score = None
    if mode == "f1":
        score = utils.get_f1(y_true, y_pred)
    if mode == "bleu":
        score = utils.get_bleu(y_true, y_pred, bleu_weight=[0,1,0,0]) 
    return score


def batch_evaluate(dev_features, dev_steps, END_id=99):
    global model, device
    '''
    :param model: model
    :param device: 数据转移到gpu
    :param dev_features: 验证集
    :param dev_steps: 验证步数
    :param END_id: 结束终结符，这里使用默认的[END]token
    '''
    f1_all, bleu_all = 0., 0.
    score_count = 0.
    with torch.no_grad():
        for i_step in tqdm(range(dev_steps)):
            origin_batch_features = copy.deepcopy(dev_features[i_step * args.eval_batch_size:  (i_step + 1) * args.eval_batch_size])
            batch_features = list(origin_batch_features)

            # 保证batch内所有样本验证完毕才算结束
            while len(batch_features) > 0:
                input_ids_np = torch.tensor(np.array([f['input_ids'] for f in batch_features]), dtype=torch.long).to(device=device)
                input_mask_np = torch.tensor(np.array([f['input_mask'] for f in batch_features]), dtype=torch.long).to(device=device)
                context_mask_np = torch.tensor(np.array([f['context_mask'] for f in batch_features]), dtype=torch.long).to(device=device)
                segment_ids_np = torch.tensor(np.array([f['segment_ids'] for f in batch_features]), dtype=torch.long).to(device=device)
                output_idx_np = torch.tensor(np.array([f['output_idx'] for f in batch_features]), dtype=torch.long).to(device=device)
                pred_logits = model(input_ids=input_ids_np, 
                                    token_type_ids=segment_ids_np, 
                                    attention_mask=input_mask_np, 
                                    context_mask=context_mask_np,
                                    output_idx = output_idx_np, 
                                    is_train=False)
                pred_logits = pred_logits.cpu().numpy()
                pred_ids = np.argmax(pred_logits, axis=1)
                new_batch_features = []
                for j in range(len(batch_features)):
                    batch_idx = batch_features[j]["batch_idx"]
                    target = batch_features[j]["output_idx"][0] + 1  # 生成下一个字,target偏移
                    origin_batch_features[batch_idx]["pred_ids"].append(pred_ids[j])
                    if target < (args.max_a_length + args.max_b_length) and pred_ids[j] != END_id:  # 如果未到长度上限，且不是[END], 继续生成
                        batch_features[j]["input_ids"][target] = pred_ids[j]
                        batch_features[j]["input_mask"][target] = 1
                        batch_features[j]["segment_ids"][target] = 1
                        batch_features[j]["output_idx"] = [target]
                        new_batch_features.append(batch_features[j])
                batch_features = new_batch_features

            # id2token
            with open(args.log_result_file, "w") as aw:
                aw.write("----------------begin to eval----------------\n")
                for i in range(len(origin_batch_features)):
                    pred_tokens = tokenizer.convert_ids_to_tokens(origin_batch_features[i]["pred_ids"])
                    pred_text = []
                    for token in pred_tokens:
                        if token == "[END]":
                            break
                        pred_text.append(token)
                    pred_text = utils.combine_tokens(pred_text)
                    pred_text = " ".join(pred_text.split()) 
                    f1_now = get_score(origin_batch_features[i]["true_text"], pred_text, mode="f1")
                    bleu_now = get_score(origin_batch_features[i]["true_text"], pred_text, mode="bleu")
                    if f1_now is not None and bleu_now is not None:
                        f1_all += f1_now
                        bleu_all += bleu_now
                        score_count += 1
                        # save
                        print_sent = tokenizer.convert_ids_to_tokens(origin_batch_features[i]["input_ids"])
                        print_sent = utils.combine_tokens(print_sent)
                        print_sent = " ".join(print_sent.split())
                        aw.write("Sentence: {}\nTrue: {}\nPred: {}\n\n".format(print_sent, origin_batch_features[i]["true_text"], pred_text))
                aw.write("----------------end to eval----------------\n")
    return f1_all/score_count, bleu_all/score_count


# Train
##############################################################################################
def learn(train_features=None, train_dataloader=None, eval_features=None):
    global args, tokenizer, model, n_gpu, device
    assert train_features and train_dataloader and eval_features
    
    print("***** Pre-Settings *****")
    # set steps
    steps_per_epoch = len(train_features) // args.batch_size
    if len(train_features) % args.batch_size != 0:
        steps_per_epoch += 1
    eval_steps_per_epoch = len(eval_features) // args.eval_batch_size
    if len(eval_features) % args.eval_batch_size != 0:
        eval_steps_per_epoch += 1
    total_steps = steps_per_epoch * args.train_epochs
    print("steps per epoch:", steps_per_epoch)
    print("total steps:", total_steps)
    print("'warmup steps:", int(args.warmup_rate * total_steps))
    
    # set optimization
    no_decay = ["bias", "LayerNorm.weight", "layer_norm.weight"]
    optimizer_grouped_parameters = [
        {"params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
        "weight_decay": args.weight_decay_rate},
        {"params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 
        "weight_decay": 0.0}
    ]
    optimizer = AdamW(optimizer_grouped_parameters, lr=args.lr, eps=1e-8)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(args.warmup_rate * total_steps), num_training_steps=total_steps)
    
    # amp init
    if args.float16:
        try:
            from apex import amp
        except ImportError:
            raise ImportError("Please install apex from https://www.github.com/nvidia/apex to use fp16 training.")
        model, optimizer = amp.initialize(model, optimizer, opt_level="O1")
    
    # do paralleling
    if n_gpu > 1:
        model = torch.nn.DataParallel(model)
    
    print("***** Training *****")
    model.train()
    global_steps = 0
    best_score = 0.
    for i in range(int(args.train_epochs)):
        print("Starting epoch %d" % (i + 1))
        start_time = time()
        loss_values = []
        for step, batch in enumerate(train_dataloader):
            batch = tuple(t.to(device) for t in batch)
            input_ids, input_mask, segment_ids, context_mask = batch
            _, loss = model(input_ids=input_ids, 
                             token_type_ids=segment_ids, 
                             attention_mask=input_mask, 
                             context_mask=context_mask,
                             is_train=True)
            if n_gpu > 1:
                loss = loss.mean()  # mean() to average on multi-gpu.
            loss_values.append(loss.item())
            if args.float16:
                with amp.scale_loss(loss, optimizer) as scaled_loss:
                    scaled_loss.backward()
            else:
                loss.backward()
                
            if args.float16:
                torch.nn.utils.clip_grad_norm_(amp.master_params(optimizer), args.clip_norm)
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.clip_norm)
                
            # update learning rate schedule
            optimizer.step()
            scheduler.step()
            model.zero_grad()
            global_steps += 1

            if global_steps % args.log_interval == 0:
                show_str = 'Epoch:{}, Steps:{}/{}, Loss:{:.4f}'.format(i + 1, global_steps, total_steps, np.mean(loss_values))
                with open(args.log_file, 'a') as aw:
                    aw.write("Epoch:{}, Steps:{}/{}, Loss:{:.4f}".format(i + 1, global_steps, total_steps, np.mean(loss_values)) + '\n')
                if global_steps > 1:
                    remain_seconds = (time() - start_time) * ((steps_per_epoch - step) / (step + 1e-5))
                    m, s = divmod(remain_seconds, 60)
                    h, m = divmod(m, 60)
                    remain_time = " remain:%02d:%02d:%02d" % (h, m, s)
                    show_str += remain_time
                print(show_str)

        # evaluate
        print("***** Evaluating *****")
        now_f1, now_bleu = batch_evaluate(eval_features, eval_steps_per_epoch)
        print("THE EPOCH f1={}, bleu-2={}.".format(now_f1, now_bleu))
        with open(args.log_file, 'a') as aw:
            aw.write("Epoch:{}, now f1 score:{:.4f}, bleu-2 score:{:.4f}.".format(i + 1, now_f1, now_bleu))
            # update optimal parameters
            if now_f1 > best_score:
                best_score = now_f1
                model_to_save = model.module if hasattr(model, 'module') else model
                torch.save(model_to_save, args.checkpoint_dir + '/best_model.pth')
                aw.write(" update the best model.\n")
                aw.write(" ---------------------------------------------------- \n")
            else:
                aw.write("keep the old model.\n")
                aw.write(" ---------------------------------------------------- \n")
        model.train()
    
    print("*"*30)
    print("Train-{}, Dev-{}".format(len(train_features), len(eval_features)))
    print('Best F1:', best_score)
    print()
    
    return best_score
   

# Main
##############################################################################################
if __name__ == '__main__':
    train_features, train_dataloader, dev_features = prepare_for_train()
    learn(train_features, train_dataloader, dev_features)   
