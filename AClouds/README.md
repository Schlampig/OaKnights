# 角色词云
*by KuyiKing*

> 这个小课题将使用明日方舟PRTS的干员图像和文本数据，使用聚类、分词和词云算法，生成角色词云，支持自定义关键词功能。


## 效果

### 刻刀（原图→词云→添加自定义关键词的词云）
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_BeesWax.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Glaucus.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Indigo.jpg" height=45% width=45% /></center>
</br>

### 嵯峨
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_BeesWax.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Glaucus.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Indigo.jpg" height=45% width=45% /></center>
</br>

### 刻俄柏
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_BeesWax.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Glaucus.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Indigo.jpg" height=45% width=45% /></center>
</br>

### 史尔特尔
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_BeesWax.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Glaucus.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Indigo.jpg" height=45% width=45% /></center>
</br>

## 步骤

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 主要软件或模型的版本如下：
  - Python 3.6.2
  - jieba 0.39
  - numpy 1.16.3
  - matplotlib 2.2.3
  - PIL 5.0.0
  - sklearn 0.18.2
  - wordcloud 1.7.0

### 2 文件架构
```
---> dictionary ---> stopwords.txt  # 存放停用词词典
              | ---> terrawords.json  # 存放泰拉专有词词典
              | ---> build_terra_dictionay.py  # 生成泰拉专有词词典的脚本，可独立于该课题外使用
 |-> font --->  FZSuHJW.TTF  # 存放词云使用的字体文件，本课题目前使用免费的方正速黑字体库
 |-> img --->  XXX.jpg  # 存放作为词云底层轮廓的角色图片，建议使用.jpg格式且不超过1MB的图
 |-> text ---> XXX.txt  # 存放角色相关文本语料
 |-> results ---> XXX.jpg  # 提供的示例效果图，不是直接由脚本生成、存储的（若需要，可修改代码自动存图）
 create_cloud.py  # 生成词语的代码
```

### 3 准备数据
  * 词云轮廓：下载[明日方舟 PRTS](https://prts.wiki/)干员页面的立绘图，该图片一般为.png格式，处理为.jpg并压缩至1MB以内为宜。为避免轮廓和色彩混乱，建议使用精一立绘。
  * 泰拉词典：基于[明日方舟 PRTS](https://prts.wiki/)“扩展→词汇一览”与“档案→角色真名”页面的信息，使用[build_terra_dictionay.py]()脚本自动构建泰拉关键词词典，增加分词准确性，可用于各种文本预处理任务。
  * 词云文案：下载[明日方舟 PRTS](https://prts.wiki/)干员页面的“干员档案”和“语音记录（中文）”文本，存放在.txt格式文档中。
  * 自定义关键词：可选择在词云文案中加入自定义关键词，方法是在脚本[create_cloud.py]()中直接通过字典结构定义关键词输入，格式为{关键词：关键词在词云文案中出现的次数}。

### 4 构建词云
  * 构建文案：输入词云文案（可视为一个长字符串），经过分词（加入泰拉词典以增强准确性）、去停用词处理后，在文案中加入自定义关键词（如果不设置，则默认不使用），最后将文案词袋用空格相连、拼接成用于生成词语的字符串即可。
  * 构建轮廓图：输入原始.jpg格式的例会图，在脚本[create_cloud.py]()的方法**img_to_colormap**中，使用[K均值聚类算法](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans)将例会图中的色谱大致分为K类作为词云中关键字的颜色。
  * 构建词云：在脚本[create_cloud.py]()的方法**get_cloud**中，将预处理好的文案与轮廓图数据输入wordcloud库的方法**WordCloud**中构建词云，再由matplotlib库的方法**imshow**显示。

### 5 运行程序
  * 本课题全部方法均写在[create_cloud.py]()中，且已提前存入词典、部分干员文案与图像，所以直接运行脚本即可。
    ```bash
    python create_cloud.py
    ```

### 6 参考资料
  * [WordCloud库使用文档](https://amueller.github.io/word_cloud/) by Andreas Mueller.
  * [词云项目wordCloud](https://github.com/fuqiuai/wordCloud) by Qiuai Fu.
  * [词云项目wordcloud](https://github.com/fyuanfen/wordcloud) by fyuanfen.

## 更新截点
2022年7月17日，词云课题本身无需在意截点，泰拉词典的信息更新至[绿野幻梦](https://prts.wiki/w/%E7%BB%BF%E9%87%8E%E5%B9%BB%E6%A2%A6)活动。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
