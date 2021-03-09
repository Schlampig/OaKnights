import json
from pprint import pprint
null = None  # json转python时将null转为None


def id2story(s):
    pass  # 预期将章节名与解包后的章节id做一个映射，优化体验
    return s


def get_operator_info(load_path):
    with open(load_path, "r") as f:
        d_all = json.load(f)
    print("- 提取干员信息 -")
    lst = list()  # lst = [d1, d2, ...] where di = {"person":person_code, "prefix":string, "content": string}
    lst_person = list()  # record person code
    for person_code, person_info in d_all.items():
        birth_month, birth_day = person_info.get("出生月", None), person_info.get("出生日", None)
        if isinstance(birth_month, int) and isinstance(birth_day, int):
            d = {"person": person_code,
                 "prefix": "",
                 "content": person_code + "的出生日期为：" + str(birth_month) + "月" + str(birth_day) + "日"}
            lst.append(d)
        for attr, value in person_info.items():
            if attr == "语音记录":
                for situation, language_type in value.items():
                    for language, voice in language_type.items():
                        if isinstance(situation, str) and isinstance(language, str) and isinstance(voice, str):
                            d = {"person": person_code,
                                 "prefix": "",
                                 "content": person_code + "在" + situation + "的语音记录中曾用" + language + "说过：" + voice}
                            lst.append(d)
            elif attr == "人物履历":
                for paragraph in value.split("\n"):
                    for sentence in paragraph.split("。"):
                        sentence = sentence.strip()
                        if len(sentence) > 0:
                            d = {"person": person_code,
                                 "prefix": "",
                                 "content": "关于" + person_code + ": " + sentence}
                            lst.append(d)
            elif attr == "是否为感染者":
                if value == "感染者":
                    description = "感染"
                else:
                    description = "未感染"
                d = {"person": person_code,
                     "prefix": "",
                     "content": person_code + "的感染状况: " + description}
                lst.append(d)
            else:
                a = person_code + "的" + attr + "为："
                if value is not None:
                    v = str(value)
                    v = v.strip()
                else:
                    continue
                if len(v) == 0:
                    continue
                if attr == "潜能描述":
                    v = "，".join([str(k)+": "+str(v) for k, v in value.items()])
                if attr == "能力标签":
                    v = "，".join(value)
                if attr == "战斗经验":
                    v = str(value) + "年"
                if attr in ["出生日", "出生月"]:
                    continue
                d = {"person": person_code,
                     "prefix": "",
                     "content": a + v}
                lst.append(d)
        lst_person.append(person_code)
    lst_person = list(set(lst_person))
    print("- 提取完成 -")
    return lst, lst_person


def find_person(content, lst_person):
    """
    在content中寻找lst_person里出现过的人
    :param content: string, 对话内容
    :param lst_person: list, 干员代号列表
    :return: list, lst_p = [干员代号, ...], 出现在content中的干员们
    """
    lst_p = list()
    for person in lst_person:
        if person in content:
            lst_p.append(person)
    return lst_p


def get_story_info(load_path, lst_person):
    with open(load_path, "r") as f:
        d_all = json.load(f)
    print("- 提取故事信息 -")
    lst = list()  # lst = [d1, d2, ...] where di = {"person":person_code, "prefix":string, "content": string}
    for story_type, story in d_all.items():
        for chapter_name, chapter_content in story.items():
            for lst_dialogue in chapter_content.get("对话正文", []):
                for dialogue in lst_dialogue:
                    split_dialogue = dialogue.split(":")
                    if len(split_dialogue) == 2:
                        person, talk = split_dialogue[0], split_dialogue[1]
                        d = {"person": person,
                             "prefix": "在" + story_type + "的" + id2story(chapter_name) + "章节，" + person + "曾说：",
                             "content": talk}
                        lst.append(d)
                        for p in find_person(talk, lst_person):
                            d = {"person": p,
                                 "prefix": "在" + story_type + "的" + id2story(chapter_name) + "章节，" + p + "曾被" + person + "提及：",
                                 "content": talk}
                            lst.append(d)
                    elif len(split_dialogue) == 1 and len(split_dialogue[0]) > 0:
                        talk = split_dialogue[0]
                        d = {"person": "NoPerson",
                             "prefix": "在" + story_type + "的" + id2story(chapter_name) + "章节，曾描述：",
                             "content": talk}
                        lst.append(d)
                        for p in find_person(talk, lst_person):
                            d = {"person": p,
                                 "prefix": "在" + story_type + "的" + id2story(chapter_name) + "章节，" + p + "曾被提及：",
                                 "content": talk}
                            lst.append(d)
                    else:
                        continue
    print("- 提取完成 -")
    return lst


def get_all_info(path_operator, path_story, num_entry=-1, is_save=False):
    """
    读取干员与故事的文本信息，拆分为多项词条后存放于一个列表中，列表可存为.json格式文件
    :param path_operator: string, 干员信息文档，通常命名为operator_all.json
    :param path_story: string, 故事文本文档，通常命名为story_raw.json
    :param num_entry: int, 存储前num_entry条词条，即存储词条数目, 负数为全部存储
    :param is_save: boolean, 是否存储词条
    :return: dict, d = {"people": lst_person, "entry": lst}, where lst_person为干员中文代码列表，lst为入库词条列表
    """
    lst_operator, lst_person = get_operator_info(path_operator)
    lst = lst_operator + get_story_info(path_story, lst_person=lst_person)
    if num_entry > 0:
        d = {"entry": lst[:num_entry], "people": lst_person}
    else:
        d = {"entry": lst, "people": lst_person}
    if is_save:
        with open("es_data.json", "w") as f:
            json.dump(d, f)
    return d


if __name__ == "__main__":
    res = get_all_info(path_operator="operator_all.json",
                       path_story="story_raw.json",
                       num_entry=-1,
                       is_save=True)  # 注意这里第一次设True让数据入库，后续可改为False不必重复入库占用时间
    pprint(res["entry"][:5]+res["entry"][-5:])
    print()
    print("- 共得到{}条数据。 -".format(len(res["entry"])))

