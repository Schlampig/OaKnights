import json
import pandas as pd
from copy import deepcopy
from tqdm import tqdm

DICT_ATTR = {"代号-中文": None, "代号-英文": None, "代号-日文": None, "画师": None, "配音": None,
             "性别": None, "星座": None, "出生月": None, "出生地": None, "种族": None, "身高": None,
             "物理强度": None, "战场机动": None, "生理耐受": None, "战术规划": None, "战斗技巧": None, "源石技艺适应性": None,
             "最高速度": None, "爬坡能力": None, "制动效能": None, "通过性": None, "续航": None, "结构稳定性": None,
             "是否为感染者": None, "体细胞与源石融合率": None, "血液源石结晶密度": None,
             "信物描述": None, "职业类型": None, "活跃领域": None, "作战范围": None,
             "能力标签": None, "特性": None,
             "潜能": None,
             "再部署时长": None, "部署费用-初始": None, "部署费用-最终": None,
             "最大阻挡数": None, "攻击间隔": None, "生命上限": None, "攻击值": None, "防御值": None, "法术抗性": None,
             "稀有度": None, "是否限定": None, "上线时间": None, "获取方式": None}


def norm_potential(s):
    d = {"天赋强化": "天赋强化", "部署费用": "部署减费", "生命上限": "生命提升", "防御值": "防御加强",
         "攻击速度": "攻速加强", "再部署时间": "再部署提速", "攻击值": "攻击加强"}
    if s in d.keys():
        return d[s]
    else:
        return "未知潜能"


def get_entity_and_relation(load_path, save_entity_path, save_relation_path):
    global DICT_ATTR
    assert load_path.endswith(".json") and save_entity_path.endswith(".csv") and save_relation_path.endswith(".csv")

    print("提取实体与关系信息...")
    dict_entity = dict()  # dict_entity = {"entity_name&entity_type": entity_id}
    dict_relation = dict()  # dict_relation = {"start_entity_id&end_entity_id": relation_type}
    entity_id = 1
    with open(load_path, "r") as f:
        dict_all = json.load(f)
        for operator_code, operator_dict in tqdm(dict_all.items()):
            d_slot = deepcopy(DICT_ATTR)  # 初始化槽值

            # 生成实体
            for k_slot in d_slot.keys():
                # 填充当前干员的槽位信息
                if k_slot == "代号-中文":
                    key = operator_code + "&" + k_slot
                    if key in dict_entity.keys():
                        d_slot[k_slot] = dict_entity[key]
                    else:
                        dict_entity[key] = str(entity_id)
                        d_slot[k_slot] = str(entity_id)
                        entity_id += 1
                elif k_slot == "活跃领域":
                    lst_place = list()  # lst_place = ["罗德岛", "莱茵生命", ...]
                    if operator_dict.get("活动地点", None) is not None:
                        lst_place.append(operator_dict.get("活动地点", None))
                    if operator_dict.get("阵营-团队", None) is not None:
                        lst_place.append(operator_dict.get("阵营-团队", None))
                    if operator_dict.get("阵营-组织", None) is not None:
                        lst_place.append(operator_dict.get("阵营-组织", None))
                    lst_place = list(filter(lambda x:len(x)>0, lst_place))
                    lst_slot = list()
                    for place in lst_place:
                        key = place + "&" + k_slot
                        if key in dict_entity.keys():
                            lst_slot.append(dict_entity[key])
                        else:
                            dict_entity[key] = str(entity_id)
                            lst_slot.append(str(entity_id))
                            entity_id += 1
                    if len(lst_slot) > 0:
                        d_slot[k_slot] = lst_slot  # d_slot["活跃领域"] = [1, 2, 3]
                elif k_slot == "能力标签":
                    lst_tag = operator_dict.get(k_slot, None)  # lst_tag = ["支援", "输出", ...]
                    if lst_tag is not None and len(lst_tag) > 0:
                        lst_slot = list()
                        for tag in lst_tag:
                            key = tag + "&" + k_slot
                            if key in dict_entity.keys():
                                lst_slot.append(dict_entity[key])
                            else:
                                dict_entity[key] = str(entity_id)
                                lst_slot.append(str(entity_id))
                                entity_id += 1
                        if len(lst_slot) > 0:
                            d_slot[k_slot] = list(set(lst_slot))  # d_slot["能力标签"] = [1, 2, 3]
                elif k_slot == "特性":
                    lst_spec = operator_dict.get(k_slot, None)  # lst_spec = ["优先攻击空中单位", "恢复友方单位生命", ...]
                    if lst_spec is not None:
                        lst_spec = lst_spec.split(";")
                        lst_slot = list()
                        for spec in lst_spec:
                            key = spec + "&" + k_slot
                            if key in dict_entity.keys():
                                lst_slot.append(dict_entity[key])
                            else:
                                dict_entity[key] = str(entity_id)
                                lst_slot.append(str(entity_id))
                                entity_id += 1
                        if len(lst_slot) > 0:
                            d_slot[k_slot] = list(set(lst_slot))  # d_slot["特性"] = [1, 2, 3]
                elif k_slot == "潜能":
                    if operator_dict.get("潜能描述", None) is not None:
                        lst_slot = list()
                        for k_p in operator_dict.get("潜能描述", None).keys():
                            key = norm_potential(k_p) + "&" + k_slot
                            if key in dict_entity.keys():
                                lst_slot.append(dict_entity[key])
                            else:
                                dict_entity[key] = str(entity_id)
                                lst_slot.append(str(entity_id))
                                entity_id += 1
                            if len(lst_slot) > 0:
                                d_slot[k_slot] = list(set(lst_slot))  # d_slot["潜能"] = [1, 2, 3]
                elif k_slot == "获取方式":
                    lst_obtain = operator_dict.get(k_slot, None)  # lst_obtain = ["公开招募", "活动限定", ...]
                    if lst_obtain is not None and len(lst_obtain) > 0:
                        lst_slot = list()
                        for obtain in lst_obtain:
                            key = obtain + "&" + k_slot
                            if key in dict_entity.keys():
                                lst_slot.append(dict_entity[key])
                            else:
                                dict_entity[key] = str(entity_id)
                                lst_slot.append(str(entity_id))
                                entity_id += 1
                        if len(lst_slot) > 0:
                            d_slot[k_slot] = list(set(lst_slot))  # d_slot["获取方式"] = [1, 2, 3]
                else:
                    slot_now = operator_dict.get(k_slot, None)
                    if slot_now is not None:
                        key = str(slot_now) + "&" + k_slot
                        if key in dict_entity.keys():
                            d_slot[k_slot] = dict_entity[key]
                        else:
                            dict_entity[key] = str(entity_id)
                            d_slot[k_slot] = str(entity_id)
                            entity_id += 1

            # 生成关系
            # 单一关系处理
            if d_slot["代号-中文"] and d_slot["代号-英文"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["代号-英文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "英文代号"
                id_tempor = d_slot["代号-英文"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["代号-日文"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["代号-日文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "日文代号"
                id_tempor = d_slot["代号-日文"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["画师"] and d_slot["代号-中文"]:
                id_tempor = d_slot["画师"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "绘制"
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["画师"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "绘制者"

            if d_slot["配音"] and d_slot["代号-中文"]:
                id_tempor = d_slot["配音"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "配音"
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["配音"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "配音者"

            if d_slot["代号-中文"] and d_slot["性别"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["性别"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "性别"
                id_tempor = d_slot["性别"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["星座"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["星座"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "星座"
                id_tempor = d_slot["星座"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["出生月"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["出生月"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "诞生月"
                id_tempor = d_slot["出生月"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["出生地"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["出生地"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "诞生地"
                id_tempor = d_slot["出生地"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["种族"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["种族"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "种族"
                id_tempor = d_slot["种族"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["身高"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["身高"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "身高"
                id_tempor = d_slot["身高"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["物理强度"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["物理强度"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "物理强度"
                id_tempor = d_slot["物理强度"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["战场机动"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["战场机动"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "战场机动"
                id_tempor = d_slot["战场机动"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["生理耐受"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["生理耐受"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "生理耐受"
                id_tempor = d_slot["生理耐受"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["战术规划"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["战术规划"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "战术规划"
                id_tempor = d_slot["战术规划"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["战斗技巧"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["战斗技巧"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "战斗技巧"
                id_tempor = d_slot["战斗技巧"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["源石技艺适应性"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["源石技艺适应性"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "源石技艺适应性"
                id_tempor = d_slot["源石技艺适应性"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["最高速度"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["最高速度"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "最高速度"
                id_tempor = d_slot["最高速度"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["爬坡能力"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["爬坡能力"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "爬坡能力"
                id_tempor = d_slot["爬坡能力"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["制动效能"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["制动效能"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "制动效能"
                id_tempor = d_slot["制动效能"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["通过性"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["通过性"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "通过性"
                id_tempor = d_slot["通过性"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["续航"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["续航"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "续航"
                id_tempor = d_slot["续航"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["结构稳定性"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["结构稳定性"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "结构稳定性"
                id_tempor = d_slot["结构稳定性"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["是否为感染者"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["是否为感染者"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "是否感染"
                id_tempor = d_slot["是否为感染者"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["体细胞与源石融合率"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["体细胞与源石融合率"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "体细胞与源石融合率"
                id_tempor = d_slot["体细胞与源石融合率"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["血液源石结晶密度"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["血液源石结晶密度"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "血液源石结晶密度"
                id_tempor = d_slot["血液源石结晶密度"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["信物描述"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["信物描述"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "信物"
                id_tempor = d_slot["信物描述"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["职业类型"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["职业类型"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "职业"
                id_tempor = d_slot["职业类型"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["作战范围"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["作战范围"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "作战范围"
                id_tempor = d_slot["作战范围"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["再部署时长"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["再部署时长"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "再部署时长"
                id_tempor = d_slot["再部署时长"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["部署费用-初始"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["部署费用-初始"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "初始费用"
                id_tempor = d_slot["部署费用-初始"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["部署费用-最终"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["部署费用-最终"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "最终费用"
                id_tempor = d_slot["部署费用-最终"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["最大阻挡数"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["最大阻挡数"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "最大阻挡数"
                id_tempor = d_slot["最大阻挡数"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["攻击间隔"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["攻击间隔"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "攻击速度"
                id_tempor = d_slot["攻击间隔"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["生命上限"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["生命上限"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "生命上限"
                id_tempor = d_slot["生命上限"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["攻击值"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["攻击值"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "攻击力"
                id_tempor = d_slot["攻击值"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["防御值"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["防御值"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "防御力"
                id_tempor = d_slot["防御值"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["法术抗性"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["法术抗性"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "法术抗性"
                id_tempor = d_slot["法术抗性"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["稀有度"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["稀有度"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "星级"
                id_tempor = d_slot["稀有度"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["是否限定"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["是否限定"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "限定情况"
                id_tempor = d_slot["是否限定"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            if d_slot["代号-中文"] and d_slot["上线时间"]:
                id_tempor = d_slot["代号-中文"] + "&" + d_slot["上线时间"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "上线时间"
                id_tempor = d_slot["上线时间"] + "&" + d_slot["代号-中文"]
                if id_tempor not in dict_relation.keys():
                    dict_relation[id_tempor] = "干员代号"

            # 拆分关系处理
            if d_slot["代号-中文"] and d_slot["特性"]:
                for i in d_slot["特性"]:
                    id_tempor = d_slot["代号-中文"] + "&" + i
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "特性"
                    id_tempor = i + "&" + d_slot["代号-中文"]
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "特性"

            if d_slot["代号-中文"] and d_slot["能力标签"]:
                for i in d_slot["能力标签"]:
                    id_tempor = d_slot["代号-中文"] + "&" + i
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "能力标签"
                    id_tempor = i + "&" + d_slot["代号-中文"]
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "能力标签"

            if d_slot["代号-中文"] and d_slot["活跃领域"]:
                for i in d_slot["活跃领域"]:
                    id_tempor = d_slot["代号-中文"] + "&" + i
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "活跃领域"
                    id_tempor = i + "&" + d_slot["代号-中文"]
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "活跃领域"

            if d_slot["代号-中文"] and d_slot["潜能"]:
                for i in d_slot["潜能"]:
                    id_tempor = d_slot["代号-中文"] + "&" + i
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "潜能"
                    id_tempor = i + "&" + d_slot["代号-中文"]
                    if id_tempor not in dict_relation.keys():
                        dict_relation[id_tempor] = "潜能"

    # 生成entity与relation的list
    print("生成实体列表...")
    lst_entity_id, lst_entity_name, lst_entity_label = list(), list(), list()
    for k_e, v_e in dict_entity.items():
        e_name, e_label = k_e.split("&")
        lst_entity_id.append(v_e)
        lst_entity_name.append(e_name)
        lst_entity_label.append(e_label)
    assert len(lst_entity_id) == len(lst_entity_name) == len(lst_entity_label)

    print("生成关系列表...")
    lst_re_start, lst_re_end, lst_re_type, lst_re_name, = list(), list(), list(), list()
    for k_r, v_r in dict_relation.items():
        r_start, r_end = k_r.split("&")
        lst_re_start.append(r_start)
        lst_re_end.append(r_end)
        lst_re_type.append(v_r)
        lst_re_name.append(v_r)
    assert len(lst_re_start) == len(lst_re_end) == len(lst_re_type) == len(lst_re_name)

    # 存储实体与关系为.csv格式文件
    print("存储实体与关系列表...")
    df_entity = pd.DataFrame({":ID(node)": lst_entity_id, "name": lst_entity_name, ":LABEL": lst_entity_label})
    df_entity = df_entity[[":ID(node)", "name", ":LABEL"]]
    df_entity.to_csv(save_entity_path, index=False, encoding="utf-8-sig")

    df_relation = pd.DataFrame({":START_ID(node)": lst_re_start, ":END_ID(node)": lst_re_end, ":TYPE": lst_re_type, "name": lst_re_name})
    df_relation = df_relation[[":START_ID(node)", ":END_ID(node)", ":TYPE", "name"]]
    df_relation.to_csv(save_relation_path, index=False, encoding="utf-8-sig")

    print("- 执行完毕 -")
    return None


if __name__ == "__main__":
    get_entity_and_relation(load_path="operator_all.json",
                            save_entity_path="operator_entity.csv",
                            save_relation_path="operator_relation.csv")
