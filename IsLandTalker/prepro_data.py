import os
import re
import json
import math
import numpy as np
from tqdm import tqdm


# 结构化原始文本
################################################################################################
def clean_text(s):
    """
    清洗对话正文
    :param s: 对话正文
    :return: string, 清洗后的对话正文
    """
    s = re.sub(r"{@[Nn]ickname}", "博士", s)
    s = s.replace("Dr.博士", "博士").replace("博士博士", "博士")
    s = s.strip().replace("[name=\"", "").replace("\"]", ":")
    # 替换破折号
    s = s.replace("——", "--")
    if "--" in s:
        s = re.sub("--+", "--", s)
    # 替换引号
    s = s.replace("“", "\"").replace("”", "\"")
    s = s.replace("‘", "\"").replace("’", "\"")
    # 替换省略号
    s = s.replace("...", "……")
    if "……" in s:
        s = re.sub("…+", "……", s)
        if s == "……":
            s = "(沉默)"
        else:
            s = s.lstrip("……")
            s = s.replace("……", "，")
            if s.endswith("，"):
                s = s[:-1] + "……"
        s = s.replace("，）", "）").replace("，)", ")")
        s = s.replace("（，", "（").replace("(，", "(")
        s = s.replace("，？", "？").replace("，?", "?")
        s = s.replace("，！", "！").replace("，!", "!")
    return s


def clean_sentence(s_raw):
    """
    清洗对话行，对话行=说话人:对话正文
    :param s_raw: 原始对话行
    :return: 清洗后对话行
    """
    s_raw = re.sub("\s+", "", s_raw)
    s_raw = s_raw.strip().replace("[name=\"", "").replace("\"]", ":")
    lst_s = s_raw.split(":")
    s_new = s_raw
    if len(lst_s) == 2:
        s_head, s_tail = lst_s[0].strip(), lst_s[1]
        s_tail = clean_text(s_tail)
        s_new = s_head + ":" + s_tail
    return s_new


def parser_file(path_dialogue, path_abstract):
    """
    从对话相关文件中结构化对话内容
    :param path_dialogue: string, 对话正文.txt文件地址
    :param path_abstract: string，对话概述.txt文件地址
    :return: dictionary, d_file = {"对话概述": string/None, "对话正文":[lst, ...]}, where lst = [对话, 对话, ...]
    """
    d_file = {"对话概述": None, "对话正文": None}
    # 获取对话概述
    try:
        with open(path_abstract, "r") as f:
            raw_abstract = f.read()
            raw_abstract = re.sub("\s+", "", raw_abstract)
            d_file["对话概述"] = raw_abstract
    except:
        pass
    # 获取对话正文
    lst_diag = list()
    with open(path_dialogue, "r") as f:
        raw_diag = f.read()
        lst_scene = raw_diag.split("[Dialog]\n")
        for scene in lst_scene:
            lst_sent = list()
            for sentence in scene.split("\n"):
                if "[name=" in sentence:
                    sentence = clean_sentence(sentence)
                    if len(sentence) > 0:
                        lst_sent.append(sentence)
            if len(lst_sent) > 0:
                lst_diag.append(lst_sent)
    if len(lst_diag) > 0:
        d_file["对话正文"] = lst_diag
    return d_file


def parser_dir(root_dir, file_type="主线"):
    """
    获取主线、悖论模拟、活动其中一种游戏类型下所有相关文件中结构化的对话内容
    :param root_dir: string, 存放文件的主路径，即ArknightsData-master/zh-CN/gamedata/story
    :param file_type: 选择解析哪类文件：主线/悖论模拟/活动
    :return: dictionary, d_dir = {"对话文件ID": {"对话概述": string/None, "对话正文":[lst, ...]}, ...}, where lst = [对话, ...]
    """
    # 获取所有对话/概述文件路径并一一对应
    print("- 获取文件地址 -")
    dict_file = dict()
    if file_type == "主线":
        for file_name in os.listdir(os.path.join(root_dir, "obt/main")):
            if file_name.endswith(".txt"):
                if file_name not in dict_file.keys():
                    dict_file[file_name.strip(".txt")] = {"对话正文路径": os.path.join(root_dir, "obt/main", file_name),
                                                          "对话概述路径": os.path.join(root_dir, "[uc]info/obt/main", file_name)}
    elif file_type == "悖论模拟":
        for file_name in os.listdir(os.path.join(root_dir, "obt/memory")):
            if file_name.endswith(".txt"):
                if file_name not in dict_file.keys():
                    dict_file[file_name.strip(".txt")] = {"对话正文路径": os.path.join(root_dir, "obt/memory", file_name),
                                                          "对话概述路径": os.path.join(root_dir, "[uc]info/obt/memory", file_name)}
    elif file_type == "活动":
        for dir_name in os.listdir(os.path.join(root_dir, "activities")):
            if not dir_name.startswith("."):
                for file_name in os.listdir(os.path.join(root_dir, "activities", dir_name)):
                    if file_name.endswith(".txt"):
                        if file_name not in dict_file.keys():
                            dict_file[file_name.strip(".txt")] = {"对话正文路径": os.path.join(root_dir, "activities", dir_name, file_name),
                                                                  "对话概述路径": os.path.join(root_dir, "[uc]info/activities", dir_name, file_name)}
    else:
        raise KeyError("[ERROR] Incorrect File Type. [主线/悖论模拟/活动]")
    # 根据对话/概述文件路径逐个解析对话文本
    if len(dict_file) == 0:
        raise KeyError("[ERROR] Empty file. ")
    print("- 解析文件内容 -")
    d_dir = dict()
    for k, v in tqdm(dict_file.items()):
        d_now = parser_file(path_dialogue=v.get("对话正文路径", ""), path_abstract=v.get("对话概述路径", ""))
        if d_now["对话概述"] is not None and d_now["对话正文"] is not None:
            d_dir.update({k: d_now})
    print("- 解析完毕 -")
    return d_dir


def parser_all(root_dir="", is_save=True):
    """
    获取主线、悖论模拟与活动类型下所有相关文件中结构化的对话内容
    :param root_dir: string, 全文档地址
    :param is_save: boolean, 是否存储解析后的对话数据
    :return: all_data = {"主线": {"主线ID": d, ...},
                         "悖论模拟": {"故事ID": d, ...},
                         "活动":{"活动ID": d, ... }}
             where d = {"对话概述": string/None, "对话正文":[lst, ...]},
             where lst = [对话, 对话, ...]
    """
    if len(root_dir) == 0:
        raise ValueError("[ERROR] Wrong data path [should be like 'ArknightsData-master/zh-CN/gamedata/story'].")
    d_all = dict()
    print("- 解析主线 -")
    d_all["主线"] = parser_dir(root_dir, file_type="主线")
    print()
    print("- 解析悖论模拟 -")
    d_all["悖论模拟"] = parser_dir(root_dir, file_type="悖论模拟")
    print()
    print("- 解析活动 -")
    d_all["活动"] = parser_dir(root_dir, file_type="活动")
    print()
    if is_save:
        print("- 存储数据中 -")
        with open("story_raw.json", "w") as f:
            json.dump(d_all, f, indent=2, ensure_ascii=False)
    print("- 执行完毕 -")
    return d_all


# 处理文本为训练、验证数据集
################################################################################################
def group_dialogue(lst):
    """
    聚合同一说话人的连续对话正文
    :param lst: list, 记录所有对话人的列表，[dialogue, ...] where dialogue = "person:context"
    :return: list, lst_new = [dialogue_new, ...], where contexts from same person have been grouped in each dialogue_new
    """
    lst_new = list()
    tag = None  # 记录当前说话人
    talk = ""  # 记录当前说话人的谈话内容
    for dialogue in lst:
        person, context = dialogue.split(":")
        if tag is None:
            tag = person
            talk += context
        else:
            if tag == person:
                talk += context
            else:
                dialogue_new = tag + ":" + talk
                tag = person
                talk = context
                dialogue_new = dialogue_new.replace("（", "(").replace("）", ")").replace(")(", "")
                lst_new.append(dialogue_new)
    return lst_new


def avg_dialogue(lst, avg_len=32):
    """
    无视角色，尽量平均拼接对话正文
    :param lst: list, 记录所有对话人的列表，[dialogue, ...] where dialogue = "person:context"
    :param avg_len: int, 列表每个项的长度
    :return: list, lst_new = [context, ...],  where contexts have similar length
    """
    lst_new = list()
    talk = ""  # 记录当前列表片段的谈话内容
    for dialogue in lst:
        _, context = dialogue.split(":")
        if len(talk) < avg_len:
            talk += context
        else:
            lst_new.append(talk)
            talk = context
    return lst_new


def group_avg_dialogue(lst, avg_len=32, min_len=16, see_talker=False):
    """
    聚合同一说话人的连续对话正文，并尽量平均拼接对话正文
    :param lst: list, 记录所有对话人的列表，[dialogue, ...] where dialogue = "person:context"
    :param avg_len: int, 列表每个项的长度
    :param min_len: int, 当前正文小于该值则直接略过，避免纯省略号、感叹号情况频繁出现
    :param see_talker: boolean, True for 'tag:talk', while False for only 'talk'
    :return: list, lst_new = [context, ...],  where contexts have similar length and belong to corresponding same person
    """
    lst_new = list()
    tag = None  # 记录当前说话人
    talk = ""  # 记录当前说话人的谈话内容
    for dialogue in lst:
        person, context = dialogue.split(":")
        tempor = context.replace("--", "").replace("……", "").replace("!", "").replace("?", "").replace("！", "").replace("？", "")
        if len(tempor) < min_len:
            continue
        if tag is None:
            tag = person
            talk += context
        else:
            if tag == person:
                if len(talk) > avg_len:
                    talk = talk.replace("（", "(").replace("）", ")").replace(")(", "")
                    talk = talk.replace("----", "--").replace("…………", "……")
                    if see_talker:
                        talk = tag + ":" + talk
                    lst_new.append(talk)
                    talk = context
                else:
                    talk += context
            else:
                talk = talk.replace("（", "(").replace("）", ")").replace(")(", "")
                talk = talk.replace("----", "--").replace("…………", "……")
                if see_talker:
                    talk = tag + ":" + talk
                lst_new.append(talk)
                tag = person
                talk = context
    return lst_new


def filter_background(s):
    """
    过滤对话中的旁白
    :param s: string, "person:context" or ":context"
    :return: boolean, True to keep, while False to discard
    """
    lst_s = s.split(":")
    if len(lst_s) == 2:
        if len(lst_s[0]) > 0 and len(lst_s[1]) > 0:
            return True
    return False


def split_story(load_path, save_path, ratio=0.8, operation="group"):
    """
    将parser_all得到的d_all数据展平为训练与验证数据
    :param load_path: string, d_all的文件路径
    :param save_path: string, 生成的训练集与验证集的根路径
    :param ratio: float, 训练集与测试集的比例
    :param operation: string, group: 同一个人说的数句话合并成一个item；avg:所有话合在一起按句子长度平均分。
    :return: list, list, train_sentence/dev_sentence=[sentence, ...], where sentence = "person:text"
    """
    print("- 开始构建 -")
    # 展平列表
    with open(load_path, "r") as f:
        d_all = json.load(f)
        d_new = d_all["主线"]
        d_new.update(d_all["悖论模拟"])
        d_new.update(d_all["活动"])
        lst_sentence = None
        for dialogue in d_new.values():
            for scene in dialogue["对话正文"]:
                if lst_sentence is None:
                    lst_sentence = scene
                else:
                    lst_sentence.extend(scene)
        lst_sentence = list(filter(lambda x: filter_background(x), lst_sentence))
        if operation == "group":
            lst_sentence = group_dialogue(lst_sentence)
        if operation == "avg":
            lst_sentence = avg_dialogue(lst_sentence)
        if operation == "group_avg":
            lst_sentence = group_avg_dialogue(lst_sentence)
        idx = math.floor(len(lst_sentence) * ratio)
        train_sentence, dev_sentence = lst_sentence[:idx], lst_sentence[idx:]
    # 统计句子长度
    lst_count = [len(dialogue) for dialogue in lst_sentence]
    max_len, min_len, avg_len = np.max(lst_count), np.min(lst_count), np.mean(lst_count)
    train_len, dev_len = len(train_sentence), len(dev_sentence)
    print("训练{}句，验证{}句。最长句含{}字，最短句含{}字，平均句长{}。".format(train_len, dev_len, max_len, min_len, avg_len))
    # 存储列表
    save_train = save_path + "_train.json"
    save_dev = save_path + "_dev.json"
    with open(save_train, "w") as f:
        json.dump(train_sentence, f, ensure_ascii=False, indent=2)
    with open(save_dev, "w") as f:
        json.dump(dev_sentence, f, ensure_ascii=False, indent=2)
    print("- 存储完毕 -")
    return train_sentence, dev_sentence


# 运行
################################################################################################
def example(do_tag=0):
    """
    数据预处理全流程示例。【注意文件路径！！！】
    :return: None
    """
    # 1. 获取一篇对话文件内容：古米有个习惯 ...
    if do_tag == 0:
        d = parser_file(path_dialogue="ArknightsData-master/zh-CN/gamedata/story/activities/act10d5/level_act10d5_st01.txt",
                        path_abstract="ArknightsData-master/zh-CN/gamedata/story/[uc]info/activities/act10d5/level_act10d5_st01.txt")
        print(d)
    # 2. 获取一类对话文件内容：获取悖论模拟类对话
    if do_tag == 1:
        d = parser_dir(root_dir="ArknightsData-master/zh-CN/gamedata/story", file_type="悖论模拟")
        print(d)
    # 3. 获取全部对话文件内容
    if do_tag == 2:
        _ = parser_all(root_dir="ArknightsData-master/zh-CN/gamedata/story")  # 注：由于打印内容过多，建议设置断点查看，而不要直接打印
    # 4. 生成训练、验证集
    if do_tag == 3:
        lst_train, lst_dev = split_story(load_path="story_raw.json", save_path="story", operation="group_avg")
        print(lst_train[:15])
        print("-"*15)
        print(lst_dev[:15])
    return None


if __name__ == "__main__":
    example(3)
