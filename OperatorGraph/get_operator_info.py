import re
import json
import socket
from bs4 import BeautifulSoup
from urllib import request, error, parse
from pprint import pprint

socket.setdefaulttimeout(60)  # 超过设置秒数则跳过该次操作


# 获取页面
##################################################################################################
def crawl_list_page(url_now):
    """
    获取干员一览页面（先在页面设置每页显示500）
    :param url_now: string, 目标页面的URL
    :return: string, 该页面的HTML文本
    """
    try:
        response = request.urlopen(url_now)
        page_now = response.read().decode("utf-8")
        return page_now
    except error.URLError as e:
        print(e.reason)
        return None


def crawl_operator_info(url_now):
    """
    获取当前干员页面
    :param url_now: string, 目标页面的URL
    :return: string, 该页面的HTML文本
    """
    try:
        response = request.urlopen(url_now)
        page_now = response.read().decode("utf-8")
        return page_now
    except error.URLError as e:
        print(e.reason)
        return None


def crawl_operator_voice(url_now):
    """
    获取当前干员语音页面，该版本脚本与crawl_operator_info方法一致，留接口供后续用
    :param url_now: string, 目标页面的URL
    :return: string, 该页面的HTML文本
    """
    try:
        response = request.urlopen(url_now)
        page_now = response.read().decode("utf-8")
        return page_now
    except error.URLError as e:
        print(e.reason)
        return None


# 处理字段细节
##################################################################################################
def normalize_fight_exp(s):
    """
    将战斗经验规范化为浮点数表示的时长，半年为0.5，不明的情况表示为None
    :param s: string，战斗经验描述
    :return: string，浮点数战斗年限
    """
    d = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
         "六": "6", "七": "7", "八": "8", "九": "9"}
    n_new = None
    if "没有" in s:
        n_new = 0.0
    if "半年" in s:
        n_new = 0.5
    if re.search(r"[一二三四五六七八九十]", s) is not None:
        n = re.search(r"[一二三四五六七八九十]+", s).group()
        if len(n) == 3:
            if n[1] == "十":
                n_new = float(d[n[0]] + d[n[2]])  # 例： 四十四->44.0
        if len(n) == 2:
            if n[0] == "十":
                n_new = float("1" + d[n[1]])  # 例：十二->12.0
            if n[1] == "十":
                n_new = float(d[n[0]] + "0")  # 例：二十->20.0
        if len(n) == 1:
            if n == "十":
                n_new = 10.0  # 例：十->10.0
            else:
                n_new = float(d[n])  # 例：五->5.0
    if "年" not in s and "月" in s:
        n_new = n_new / 12.0  # 例：三个月->3.0/12.0=0.25
    return n_new


def normalize_birth_place(s):
    """
    将出生地规范化，例如东国与东统一为东。
    :param s: string，出生地描述
    :return: string，出生地描述
    """
    if "东" in s:  # 注：炎包含"炎-龙门"、"炎-岁"等具体地名，不处理
        s = "东"
    return s


def normalize_birth(s):
    """
    将出生日规范化，例如1月23日为出生月=01，出生日=23，星座=水瓶座。
    :param s: string，出生日描述
    :return: int, int, string，出生月，出生日，星座
    """
    s_month, s_day, s_constellation = None, None, None
    s = re.sub("\s+", "", s)  # 去空格
    if re.search(r"\w+月\w+日", s) is not None:
        lst_s = re.findall(r"(\w+)月(\w+)日", s)
        s_month, s_day = int(lst_s[0][0]), int(lst_s[0][1])
        if s_month == 1:
            s_constellation = "摩羯" if s_day < 20 else "水瓶"
        if s_month == 2:
            s_constellation = "水瓶" if s_day < 19 else "双鱼"
        if s_month == 3:
            s_constellation = "双鱼" if s_day < 21 else "白羊"
        if s_month == 4:
            s_constellation = "白羊" if s_day < 20 else "金牛"
        if s_month == 5:
            s_constellation = "金牛" if s_day < 21 else "双子"
        if s_month == 6:
            s_constellation = "双子" if s_day < 22 else "巨蟹"
        if s_month == 7:
            s_constellation = "巨蟹" if s_day < 23 else "狮子"
        if s_month == 8:
            s_constellation = "狮子" if s_day < 23 else "处女"
        if s_month == 9:
            s_constellation = "处女" if s_day < 23 else "天秤"
        if s_month == 10:
            s_constellation = "天秤" if s_day < 24 else "天蝎"
        if s_month == 11:
            s_constellation = "天蝎" if s_day < 23 else "射手"
        if s_month == 12:
            s_constellation = "射手" if s_day < 24 else "摩羯"
    return s_month, s_day, s_constellation


def normalize_height(s):
    """
    将身高规范化，例如155cm为155.0，不明则为None。
    :param s: string，身高描述
    :return: float，身高值
    """
    s_new = None
    s = re.sub("\s+", "", s)  # 去空格
    if "cm" in s:
        s = s.replace("cm", "").strip()
        s_new = float(s)
    return s_new


def normalize_dimension(s):
    """
    将体质指标规范化，例如卓越为4，缺陷为0。
    :param s: string，体质指标描述
    :return: int，体质指标值
    """
    d = {"缺陷": 0., "低劣": 1., "标准": 2., "优良": 3., "卓越": 4., "???": 5.}
    s = re.sub("\s+", "", s)  # 去空格
    s_new = d.get(s, 2.)
    return s_new


def normalize_speed(s):
    """
    将速度指标规范化。
    :param s: string，速度指标描述
    :return: float，速度指标值
    """
    s = re.sub("\s+", "", s)  # 去空格
    s_new = float(s.replace("km/h", ""))
    return s_new


def normalize_tag(s):
    """
    将能力标签规范化，例如"位移 输出 控场"为["位移", "输出",  "控场"]。
    :param s: string，能力标签描述
    :return: list，能力标签列表
    """
    lst_tag = ["输出", "支援", "控场", "防护", "群攻", "减速", "削弱", "爆发", "位移",
               "新手", "治疗", "召唤", "生存", "费用回复", "快速复活", "支援机械", ]
    lst_s = [t for t in s.split() if t in lst_tag]
    return lst_s


def normalize_spec(s):
    """
    将能力特性规范化并分类打上标签，一期仅是去掉多余符号
    :param s: string，能力特性描述
    :return: string，能力特性描述
    """
    s = s.replace("color", "").replace("|", "").replace("{", "").replace("}", "").replace("<br/>", ";")
    s = re.sub("#[0-9A-Z]{6}", "", s)
    if ";(" in s:
        s = s.replace(";(", ";").replace("）", "")
    s = s.replace("，", ",").replace("；", ";").replace("。", ".").replace("（", "(").replace("）", ")")
    if "(" in s and ")" not in s:
        s = s.replace("(", "")
    if "(" not in s and ")" in s:
        s = s.replace(")", "")
    return s


def normalize_stop(s):
    """
    将阻挡数规范化为最大阻挡数，例2→3→3为3
    :param s: string，阻挡数描述
    :return: int，最大阻挡数
    """
    s = re.sub("\s+", "", s)  # 去空格
    lst_s = s.split("→")
    return int(lst_s[-1])


def normalize_cost(s):
    """
    将部署费用规范化并分成初始和最终费用返回
    :param s: string，部署费用描述
    :return: int, int，初始费用, 最终费用
    """
    s = re.sub("\s+", "", s)  # 去空格
    lst_s = s.split("→")
    lst_s = [int(c) if 0 < int(c) < 100 else None for c in lst_s]
    s_start, s_final = lst_s[0], lst_s[-1]
    return s_start, s_final


def normalize_potential(s_k, s_v):
    """
    将潜能类型及潜能值规范化并合并为潜能描述
    :param s_k: string，潜能类型描述
    :param s_v: string，潜能值描述
    :return: dict，{潜能类型(string):潜能值(float)}
    """
    d = {"res": "天赋强化", "cost": "部署费用", "hp": "生命上限", "def": "防御值",
         "interval": "攻击速度", "re_deploy": "再部署时间", "atk": "攻击值"}
    s_k = re.sub("\s+", "", s_k)  # 去空格
    s_v = re.sub("\s+", "", s_v)  # 去空格
    lst_k = s_k.replace(",,", ",").strip(",").split(",")
    lst_k = list(map(lambda x: d.get(x, "未知潜能"), lst_k))
    lst_v = s_v.replace(",,", ",").strip().split(",")
    d_s = dict()
    for k, v in zip(lst_k, lst_v):
        if k in d_s.keys():
            d_s[k] += float(v)
        else:
            d_s[k] = float(v)
    return d_s


def normalize_obtain(s):
    """
    将获取方式规范化为方式列表
    :param s: string，获取方式描述
    :return: list，获取方式列表
    """
    s_new = [s.strip() for s in s.split()]
    return s_new


def normalize_star(s):
    """
    将稀有度规范化为星级描述
    :param s: string，稀有度描述
    :return: string，星级描述
    """
    s = re.sub("\s+", "", s)  # 去空格
    s_new = str(int(s) + 1) + "星"
    return s_new


def normalize_debut(s):
    """
    将上线时间规范化为日期（删除时间）
    :param s: string，上线时间描述
    :return: string，上线日期描述
    """
    lst_s = s.split()
    return lst_s[0]


def normalize_rate(s):
    """
    将源石融合率规范化为小数，例如15%为0.15
    :param s: string，融合率描述
    :return: float，融合率值
    """
    s_new = s.strip().replace("%", "").replace("<", "").replace(">", "").strip()
    try:
        s_new = float(s_new)
    except:
        s_new = None  # 例：未公开
    return s_new


def normalize_density(s):
    """
    将结晶密度规范化为小数，例如0.23u/L为0.23
    :param s: string，结晶密度描述
    :return: string，结晶密度值
    """
    s_new = None
    s = re.sub("\s+", "", s)  # 去空格
    if "u/L" in s:
        s = s.replace("u/L", "").strip()
        s_new = float(s)
    return s_new


def normalize_pf(s):
    """
    将履历规范化。
    :param s: string，履历
    :return: string，去掉冗余字符的履历
    """
    s_new = None
    if len(s) > 0 and "】" not in s:
        s = re.sub(r"[0-9]文本=", "", s)
        s = re.sub(r"\|档案[0-9]", "", s)
        s = re.sub(r"}}\s*==语音记录==", "", s)
        s = s.replace("\n", "")
        s_new = s.strip("= ")
    return s_new


# 结构化页面信息
##################################################################################################
def parser_list_page(page_now, is_save=True):
    """
    解析干员一览页面，获取所有干员名称
    :param page_now: string, 干员一览页面的HTML文本
    :param is_save: bool, 是否存储干员列表
    :return: list, 干员代号
    """
    soup = BeautifulSoup(page_now, "lxml")
    lst = list()
    for entry in soup.find_all(name="div", attrs={"class": "smwdata"}):
        if entry.has_attr("data-cn") and len(entry["data-cn"]) > 0:
            lst.append(entry["data-cn"])
    if is_save:
        with open("operator_list.json", "w") as f:
            json.dump(lst, f)
    print("Obtain {} operators.".format(len(lst)))
    return lst


def parser_operator_info(page_now, is_car=False):
    """
    解析当前干员基本信息页面
    :param page_now: string, 当前干员页面文本
    :param is_car: bool, 当前干员是否为小车
    :return: json, 干员信息字典
    """
    d_info = dict()
    try:
        page_now = BeautifulSoup(page_now, "lxml")
        info = page_now.find(name="textarea")
        info = info.string
        # 提取干员基本信息
        if len(re.findall(r"干员名=(.*)\n", info)) == 1:
            d_info["中文代号"] = re.findall(r"干员名=(.*)\n", info)[0]
        if len(re.findall(r"干员名jp=(.*)\n", info)) == 1:
            d_info["日文代号"] = re.findall(r"干员名jp=(.*)\n", info)[0]
        if len(re.findall(r"干员外文名=(.*)\n", info)) == 1:
            d_info["英文代号"] = re.findall(r"干员外文名=(.*)\n", info)[0]
        if len(re.findall(r"画师=(.*)\n", info)) == 1:
            d_info["画师"] = re.findall(r"画师=(.*)\n", info)[0]
        if len(re.findall(r"配音=(.*)\n", info)) == 1:
            d_info["配音"] = re.findall(r"配音=(.*)\n", info)[0]
        if len(re.findall(r"性别=(.*)\n", info)) == 1:
            d_info["性别"] = re.findall(r"性别=(.*)\n", info)[0]  # 此处不是【性别】，因为小车是【设定性别】
        if len(re.findall(r"战斗经验=(.*)\n", info)) == 1:
            d_info["战斗经验"] = normalize_fight_exp(re.findall(r"战斗经验=(.*)\n", info)[0])
        if len(re.findall(r"出身地=(.*)\n", info)) == 1:
            d_info["出生地"] = normalize_birth_place(re.findall(r"出身地=(.*)\n", info)[0])
        if len(re.findall(r"日=(.*)\n", info)) == 1:
            d_info["出生月"], d_info["出生日"], d_info["星座"] = normalize_birth(re.findall(r"日=(.*)\n", info)[0])
        if len(re.findall(r"【种族】(.*)\n", info)) == 1:
            d_info["种族"] = re.findall(r"【种族】(.*)\n", info)[0]
        if len(re.findall(r"【身高】(.*)\n", info)) == 1:
            d_info["身高"] = normalize_height(re.findall(r"【身高】(.*)\n", info)[0])
        if is_car:  # 小车维度
            if len(re.findall(r"出厂时间=(.*)\n", info)) == 1:
                d_info["战斗经验"] = normalize_fight_exp(re.findall(r"出厂时间=(.*)\n", info)[0])
            if len(re.findall(r"产地=(.*)\n", info)) == 1:
                d_info["出生地"] = re.findall(r"产地=(.*)\n", info)[0]
            if len(re.findall(r"【型号】(.*)\n", info)) == 1:
                d_info["种族"] = re.findall(r"【型号】(.*)\n", info)[0]
            if len(re.findall(r"【高度】(.*)\n", info)) == 1:
                d_info["身高"] = normalize_height(re.findall(r"【高度】(.*)\n", info)[0])

        # 提取干员体质维度信息
        if len(re.findall(r"【物理强度】(.*)\n", info)) == 1:
            d_info["物理强度"] = normalize_dimension(re.findall(r"【物理强度】(.*)\n", info)[0])
        if len(re.findall(r"【战场机动】(.*)\n", info)) == 1:
            d_info["战场机动"] = normalize_dimension(re.findall(r"【战场机动】(.*)\n", info)[0])
        if len(re.findall(r"【生理耐受】(.*)\n", info)) == 1:
            d_info["生理耐受"] = normalize_dimension(re.findall(r"【生理耐受】(.*)\n", info)[0])
        if len(re.findall(r"【战术规划】(.*)\n", info)) == 1:
            d_info["战术规划"] = normalize_dimension(re.findall(r"【战术规划】(.*)\n", info)[0])
        if len(re.findall(r"【战斗技巧】(.*)\n", info)) == 1:
            d_info["战斗技巧"] = normalize_dimension(re.findall(r"【战斗技巧】(.*)\n", info)[0])
        if len(re.findall(r"【源石技艺适应性】(.*)\n", info)) == 1:
            d_info["源石技艺适应性"] = normalize_dimension(re.findall(r"【源石技艺适应性】(.*)\n", info)[0])
        if is_car:  # 小车维度
            if len(re.findall(r"【最高速度】(.*)\n", info)) == 1:
                d_info["最高速度"] = normalize_speed(re.findall(r"【最高速度】(.*)\n", info)[0])
            if len(re.findall(r"【爬坡能力】(.*)\n", info)) == 1:
                d_info["爬坡能力"] = normalize_dimension(re.findall(r"【爬坡能力】(.*)\n", info)[0])
            if len(re.findall(r"【制动效能】(.*)\n", info)) == 1:
                d_info["制动效能"] = normalize_dimension(re.findall(r"【制动效能】(.*)\n", info)[0])
            if len(re.findall(r"【通过性】(.*)\n", info)) == 1:
                d_info["通过性"] = normalize_dimension(re.findall(r"【通过性】(.*)\n", info)[0])
            if len(re.findall(r"【续航】(.*)\n", info)) == 1:
                d_info["续航"] = normalize_dimension(re.findall(r"【续航】(.*)\n", info)[0])
            if len(re.findall(r"【结构稳定性】(.*)\n", info)) == 1:
                d_info["结构稳定性"] = normalize_dimension(re.findall(r"【结构稳定性】(.*)\n", info)[0])

        # 提取干员职业信息
        if len(re.findall(r"职业=(.*)\n", info)) == 1:
            d_info["职业类型"] = re.findall(r"职业=(.*)\n", info)[0]
        if len(re.findall(r"情报编号=(.*)\n", info)) == 1:
            d_info["情报编号"] = re.findall(r"情报编号=(.*)\n", info)[0]
        if len(re.findall(r"所属国家=(.*)\n", info)) == 1:
            d_info["活动地点"] = re.findall(r"所属国家=(.*)\n", info)[0]
        if len(re.findall(r"所属团队=(.*)\n", info)) == 1:
            d_info["阵营-团队"] = re.findall(r"所属团队=(.*)\n", info)[0]
        if len(re.findall(r"所属组织=(.*)\n", info)) == 1:
            d_info["阵营-组织"] = re.findall(r"所属组织=(.*)\n", info)[0]
        if len(re.findall(r"位置=(.*)\n", info)) == 1:
            d_info["作战范围"] = re.findall(r"位置=(.*)\n", info)[0]
        if len(re.findall(r"标签=(.*)\n", info)) == 1:
            d_info["能力标签"] = normalize_tag(re.findall(r"标签=(.*)\n", info)[0])  # 能力标签的值是个list
        if len(re.findall(r"特性=(.*)\n", info)) == 1:
            d_info["特性"] = normalize_spec(re.findall(r"特性=(.*)\n", info)[0])
        if len(re.findall(r"再部署=(.*)\n", info)) == 1:
            d_info["再部署时长"] = float(re.findall(r"再部署=(.*)\n", info)[0].strip("s"))
        if len(re.findall(r"\|部署费用=(.*)\n", info)) == 1:
            d_info["部署费用-初始"], d_info["部署费用-最终"] = normalize_cost(re.findall(r"\|部署费用=(.*)\n", info)[0])
        if len(re.findall(r"\|阻挡数=(.*)\n", info)) == 1:
            d_info["最大阻挡数"] = normalize_stop(re.findall(r"\|阻挡数=(.*)\n", info)[0])
        if len(re.findall(r"攻击速度=(.*)\n", info)) == 1:
            d_info["攻击间隔"] = float(re.findall(r"攻击速度=(.*)\n", info)[0].strip("s"))
        if len(re.findall("精英2_满级", info)) >= 5:
            d_info["生命上限"] = float(re.findall(r"精英2_满级_生命上限=(.*)\n", info)[0])
            d_info["攻击值"] = float(re.findall(r"精英2_满级_攻击=(.*)\n", info)[0])
            d_info["防御值"] = float(re.findall(r"精英2_满级_防御=(.*)\n", info)[0])
            d_info["法术抗性"] = float(re.findall(r"精英2_满级_法术抗性=(.*)\n", info)[0])
        elif len(re.findall("精英1_满级", info)) >= 5:
            d_info["生命上限"] = float(re.findall(r"精英1_满级_生命上限=(.*)\n", info)[0])
            d_info["攻击值"] = float(re.findall(r"精英1_满级_攻击=(.*)\n", info)[0])
            d_info["防御值"] = float(re.findall(r"精英1_满级_防御=(.*)\n", info)[0])
            d_info["法术抗性"] = float(re.findall(r"精英1_满级_法术抗性=(.*)\n", info)[0])
        else:
            d_info["生命上限"] = float(re.findall(r"精英0_满级_生命上限=(.*)\n", info)[0])
            d_info["攻击值"] = float(re.findall(r"精英0_满级_攻击=(.*)\n", info)[0])
            d_info["防御值"] = float(re.findall(r"精英0_满级_防御=(.*)\n", info)[0])
            d_info["法术抗性"] = float(re.findall(r"精英0_满级_法术抗性=(.*)\n", info)[0])
        if len(re.findall(r"潜能=(.*)\n", info)) == 1 and len(re.findall(r"潜能类型=(.*)\n", info)) == 1:
            d_info["潜能描述"] = normalize_potential(re.findall(r"潜能类型=(.*)\n", info)[0],
                                                 re.findall(r"潜能=(.*)\n", info)[0])  # 合并潜能类型与值

        # 提取游戏信息
        if len(re.findall(r"获得方式=(.*)\n", info)) == 1:
            d_info["获取方式"] = normalize_obtain(re.findall(r"获得方式=(.*)\n", info)[0])
        if len(re.findall(r"上线时间=(.*)\n", info)) == 1:
            d_info["上线时间"] = normalize_debut(re.findall(r"上线时间=(.*)\n", info)[0])
        if len(re.findall(r"稀有度=(.*)\n", info)) == 1:
            d_info["稀有度"] = normalize_star(re.findall(r"稀有度=(.*)\n", info)[0])
        if len(re.findall(r"限定=(.*)\n", info)) == 1:
            d_info["是否限定"] = "是"
        else:
            d_info["是否限定"] = "否"

        # 提取矿石病感染情况
        if len(re.findall(r"是否感染者=(.*)\n", info)) == 1:
            d_info["是否为感染者"] = re.findall(r"是否感染者=(.*)\n", info)[0]
        if len(re.findall(r"体细胞与源石融合率=(.*)\n", info)) == 1:
            d_info["体细胞与源石融合率"] = normalize_rate(re.findall(r"体细胞与源石融合率=(.*)\n", info)[0])
        if len(re.findall(r"血液源石结晶密度=(.*)\n", info)) == 1:
            d_info["血液源石结晶密度"] = normalize_density(re.findall(r"血液源石结晶密度=(.*)\n", info)[0])

        # 提取信物与招聘信息
        if len(re.findall(r"信物描述=(.*)\n", info)) == 1:
            d_info["信物描述"] = re.findall(r"信物描述=(.*)\n", info)[0]
        if len(re.findall(r"干员简介=(.*)\n", info)) == 1:
            d_info["招聘描述"] = re.findall(r"干员简介=(.*)\n", info)[0]
        if len(re.findall(r"干员简介补充=(.*)\n", info)) == 1:
            d_info["招聘补充描述"] = re.findall(r"干员简介补充=(.*)\n", info)[0]

        # 人物档案
        s_pf = ""
        for i_pf in range(1, 9):
            s_pf += str(i_pf) + "文本=(?:.*)\|档案" + str(i_pf + 1) + "=" + "|"
        s_pf += "9文本=(?:.*)==语音记录=="
        lst_pf = re.compile(s_pf, re.S).findall(info)
        lst_profile = list()
        for pf in lst_pf:
            if normalize_pf(pf) is not None:
                lst_profile.append(normalize_pf(pf))
        d_info["人物履历"] = "\n".join(lst_profile)
    except:
        d_info = None
    return d_info


def parser_operator_voice(page_now):
    """
    解析当前干员页面
    :param page_now: string, 当前干员语音页面文本
    :return: json, 干员信息字典
    """
    page_now = BeautifulSoup(page_now, "lxml")
    table = page_now.find(name="table", attrs={"class": "wikitable nomobile"})
    table = table.tbody.children
    d_voice = None
    d_v = dict()
    for child in table:
        try:
            # 获取语音触发条件
            v_cond = child.find(name="th").b.string
            # 获取语音正文
            lst_value = [p.string for p in child.find(name="td").find_all(name="p")]
            d_v[v_cond] = {"中文": lst_value[1], "日文": lst_value[0]}
        except:
            continue
    if len(d_v) > 0:
        d_voice = {"语音记录": d_v}
    return d_voice


# 单独/批量调度结构化方法
##################################################################################################
def check_all_operator(lst_operator, is_save=True):
    """
    获取干员名录中全部干员信息
    :param lst_operator: list, 干员名录
    :param is_save: bool, 是否存储结果到
    :return: dict, 全部干员（基础+语音）信息
    """
    # 获取并解析当前干员信息
    n_operator = len(lst_operator)
    d_all = dict()
    for i_operator_code, operator_code in enumerate(lst_operator):
        print(">>>>>>>进度{}/{}  正在获取干员 {} 的信息...".format(i_operator_code+1, n_operator, operator_code))
        # 解析干员基本信息
        url_info = "http://prts.wiki/index.php?title=" + parse.quote(operator_code) + "&action=edit"
        info_now = crawl_operator_info(url_now=url_info)
        if operator_code in ["Lancet-2", "Castle-3", "THRM-EX"]:
            d_info = parser_operator_info(info_now, is_car=True)
        else:
            d_info = parser_operator_info(info_now)

        # 解析干员语音信息
        url_voice = "http://prts.wiki/w/" + parse.quote(operator_code) + "/" + parse.quote("语音记录")
        voice_now = crawl_operator_voice(url_now=url_voice)
        d_voice = parser_operator_voice(voice_now)

        # 合并干员信息
        if d_info is not None and d_voice is not None:
            d_all[operator_code] = dict(d_voice, **d_info)
        elif d_info is not None:
            d_all[operator_code] = d_info
            print("[ERROR] Operator {}: Voice Missing".format(operator_code))
        elif d_voice is not None:
            d_all[operator_code] = d_voice
            print("[ERROR] Operator {}: Information Missing".format(operator_code))
        else:
            d_all[operator_code] = None
            print("[ERROR] Operator {}: Total Missing".format(operator_code))

    # 存储全干员信息
    if is_save:
        print(">>>>>>>存储干员信息...")
        with open("operator_all.json", "w") as f:
            json.dump(d_all, f, indent=2)
    return d_all


def check_single_operator(operator_code, is_save=False):
    """
    获取单个干员信息
    :param operator_code: string, 干员代号
    :param is_save: bool, 是否存储结果到
    :return: dict, 干员（基础+语音）信息
    """
    # 获取并解析干员基本信息
    url_info = "http://prts.wiki/index.php?title=" + parse.quote(operator_code) + "&action=edit"
    info_now = crawl_operator_info(url_now=url_info)
    d_info = parser_operator_info(info_now)
    # 获取并解析干员语音信息
    url_voice = "http://prts.wiki/w/" + parse.quote(operator_code) + "/" + parse.quote("语音记录")
    voice_now = crawl_operator_voice(url_now=url_voice)
    d_voice = parser_operator_voice(voice_now)
    # 合并干员信息
    if d_info is not None and d_voice is not None:
        d_all = dict(d_voice, **d_info)
    elif d_info is not None:
        d_all = d_info
    elif d_voice is not None:
        d_all = d_voice
    else:
        d_all = None
    # 存储、显示当前干员信息
    if is_save:
        save_name = "operator_" + operator_code + ".pkl"
        with open(save_name, "w") as f:
            json.dump(d_all, f, indent=2)
    return d_all


# 以.csv形式展示
##################################################################################################
def json2csv(load_path, save_path):
    """
    将get_operator_info.py获取到的干员信息转换为.csv表格文件显示
    :param load_path:
    :param save_path:
    :return:
    """
    assert load_path.endswith(".json") and save_path.endswith(".csv")
    lst_attr = ["中文代号", "日文代号", "英文代号", "画师", "配音", "性别", "战斗经验", "出生地", "出生月", "出生日",
                "星座", "种族", "身高", "物理强度", "战场机动", "生理耐受", "战术规划", "战斗技巧", "源石技艺适应性",
                "是否为感染者", "体细胞与源石融合率", "血液源石结晶密度", "职业类型", "情报编号", "活动地点", "阵营-团队",
                "阵营-组织", "作战范围", "能力标签", "特性", "再部署时长", "部署费用-初始", "部署费用-最终", "最大阻挡数",
                "攻击间隔", "生命上限", "攻击值", "防御值", "法术抗性", "潜能", "获取方式", "上线时间", "稀有度", "是否限定",
                "信物描述", "招聘描述", "招聘补充描述", "是否支援机械", "产地", "出厂时间", "型号", "高度", "最高速度",
                "爬坡能力", "制动效能", "通过性", "续航", "结构稳定性", "人物履历"]

    fw = open(save_path, "w", encoding="utf-8-sig")
    s_title = ",".join(lst_attr)
    s_title += "\n"
    fw.write(s_title)
    with open(load_path, "r") as f:
        for k, d in json.load(f).items():
            s_row = ""
            for attr in lst_attr:
                if attr == "能力标签":
                    s_row += "&".join(d.get(attr, [])) + ","
                elif attr == "潜能":
                    if d.get("潜能描述", False):
                        s_row += "&".join([str(k)+"("+str(v)+")" for k, v in d.get("潜能描述", False).items()])  + ","
                    else:
                        s_row += ","
                elif attr == "是否支援机械":
                    if k in ["Lancet-2", "Castle-3", "THRM-EX"]:
                        s_row += "是,"
                    else:
                        s_row += "否,"
                else:
                    s_row += str(d.get(attr, "")) + ","
            s_row = s_row.strip(",") + "\n"
            fw.write(s_row)
    fw.flush()
    fw.close()
    print("- 转换完毕 -")
    return None


# 示例
##################################################################################################
def example(do_tag=2):
    """
    数据预处理全流程示例
    :return: None
    """
    print("- 开始解析 -")
    # 1. 获取并存储全部干员列表
    if do_tag in [0, 1]:
        operator_list = parser_list_page(crawl_list_page(url_now="http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"))
        print(operator_list)
    # 2-1. 输入任意干员代号，获取该干员基本&语音信息
    if do_tag in [0, 2]:
        operator_dict = check_single_operator("温蒂")
        pprint(operator_dict)
    # 2-2. 载入干员列表，获取列表中全部干员基本&语音信息
    if do_tag in [0, 3]:
        with open("operator_list.json", "r") as f:
            lst = json.load(f)
        check_all_operator(lst_operator=lst)
    # 3. 生成干员信息表格
    if do_tag in [0, 4]:
        json2csv(load_path="operator_all.json", save_path="operator_all.csv")
    print("- 执行完毕 -")
    return None


if __name__ == "__main__":
    example()
