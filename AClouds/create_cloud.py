# coding:utf-8
import json
import jieba
import random
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.cluster import MiniBatchKMeans
from wordcloud import WordCloud


def load_stop_words(file_path="./dictionary/stopwords.txt"):
    """
    载入停用词词典。
    :param file_path: string, the path of .txt file, one line for a stop word
    :return: d = {stop_word: True}
    """
    print(">>> Initializing stop-words ...")
    d = dict()
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if line not in d.keys():
                d[line] = True
    return d


STOP_WORDS = load_stop_words()


def text2words(text, d_profile={}):
    """
    清洗输入的中文文本，分词，并生成新的文本用于后续词云生成。
    :param text: string, like: "这是一个示例哈哈哈，应该没问题"
    :param d_profile: dict, 自定义加入文本的关键词，{keyword: number of keyword}
    :return: string, like: "这是 一个 示例 应该 没问题"
    """
    global STOP_WORDS

    print(">>> Initializing terra-words ...")  # 载入泰拉词典辅助增强分词，也可以写成预载入以提速
    with open("./dictionary/terrawords.json", "r") as f:
        for word in json.load(f).keys():
            jieba.add_word(word)

    print(">>> Cleaning text ...")
    lst_text = list()
    for word in jieba.lcut(text):
        if len(word) > 0 and word not in STOP_WORDS:
            lst_text.append(word)
    print(">>> Adding Self-defining keywords ...")
    for k, n_k in d_profile.items():
        for i_k in range(n_k):
            lst_text[random.randint(0, len(lst_text)-1)] = lst_text[random.randint(0, len(lst_text)-1)] + " " + k
    text_new = " ".join(lst_text)

    return text_new


def rgb_to_hex(np_rgb):
    """
    将RGB数值转为16进制表示，用于后续处理。
    :param np_rgb: ndarray, np.array([R, G, B])
    :return: string, like "#9B4842"
    """
    s_hex = '#'
    for c in np_rgb:
        num = int(c)  # 取整
        c_new = str(hex(num))[-2:].replace('x', '0').upper()  # 将当前取值整数，转化为16进制字符串
        s_hex += c_new  # 拼接
    return s_hex


def img_to_colormap(img_path, n_colors=7, re_size=-1):
    """
    提取输入图像的色谱，分n_colors段生成colormap。
    :param img_path: string, path to store the image
    :param n_colors: int, number of clusters/colors (in colormap)
    :return: colormap for matplotlib, background is a nd-array image
    """
    print(">>> Loading image ...")
    background = Image.open(img_path)
    if background.mode != "RGB":
        background = background.convert("RGB")
    if re_size > 0:
        background = background.resize((re_size, re_size))
    background = np.asarray(background)
    img = background.reshape(-1, 3).tolist()
    img_train = np.array([pixel for pixel in img if pixel != [255, 255, 255]])
    print(">>> Clustering (with sample size: {})...".format(img_train.shape))
    cluster = MiniBatchKMeans(n_clusters=n_colors, batch_size=10).fit(img_train)
    print(">>> Get ColorMap ...")
    colormap = list()
    for center in cluster.cluster_centers_:
        rgb_now = rgb_to_hex(center)
        colormap.append(rgb_now)
    colormap = ListedColormap(colormap)  # 这里可以去重，但无必要
    return colormap, background


def get_cloud(path_text, path_img, d_profile={}, font_path="./font/FZSuHJW.TTF"):
    """
    读取文本、背景图片、使用字库，生成词云图，并存储。
    :param path_text: string, path of .txt file stored corpus
    :param path_img: string, path of .jpg file stored background image
    :param d_profile: dict, 自定义加入文本的关键词，{keyword: number of keyword}
    :param font_path: string, path of .ttf file to store used font, FZSuHJW means 方正速黑（免费字体）
                              (字体获取：方正字体官网：https://www.foundertype.com/)
    :return: None
    """
    print(">>> Loading text ...")
    with open(path_text, "r") as f:
        text_raw = "".join(f.readlines())
    text = text2words(text_raw, d_profile)
    cmap, background = img_to_colormap(path_img, n_colors=7)
    print(">>> Drawing Word-Cloud (with mask size: {}) ...".format(background.shape))
    cloud = WordCloud(font_path=font_path,  # 设置字体
                      width=background.shape[1],
                      height=background.shape[0],
                      background_color="white",  # 背景颜色
                      colormap=cmap,
                      max_words=1111,  # 词云显示的最大词数
                      mask=background,  # 设置背景图片
                      random_state=42)
    cloud.generate(text)
    # show cloud
    plt.figure()
    plt.imshow(cloud)
    plt.axis("off")
    plt.show()  # 注：这里可以在生成的图片里截图，也可以加一行save代码存图
    print(">>> Done")
    return None


if __name__ == "__main__":
    # 自定义关键词
    kw_刻刀 = {"吃我四刀": 50, "合成玉拟人": 40, "厨房杀手": 30, "The World": 20, "别拉耳朵": 10}
    kw_嵯峨 = {"饿哦饭饭": 40, "纳豆拌饭": 30, "六根香蕉": 30, "油炸豆腐": 30, "劝善": 20, "小僧":10}
    kw_史尔特尔 = {"你42奶奶": 42, "死ね": 35, "冰淇淋": 25, "真神": 20, "强度第一排": 15, "清小怪": 15}
    kw_刻俄柏 = {"哒哒哒哒哒": 40, "饿了": 40, "厨房禁入": 35, "独行长路": 35, "很傻的狗": 25, "很热的刀": 15, "很冰的斧": 15, "很重的枪": 15}

    # 示例
    get_cloud(path_text="./text/刻俄柏.txt", path_img="./img/刻俄柏.jpg", d_profile=kw_刻俄柏)
    # 不使用自定义关键词:
    # get_cloud(path_text="./text/刻俄柏.txt", path_img="./img/刻俄柏.jpg", d_profile={})
