# 问泰拉
*by KuyiKing*

> 这个小课题将干员信息与游戏剧本数据整理入库，使用简单的全文检索服务，根据用户输入问题，反馈库中匹配到的答案，实现伪问答系统。


## 效果

### 提问干员信息
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/xxx.png" height=35% width=35% /></center>

### 查找剧本内容
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/xxx.png" height=35% width=35% /></center>

## 步骤

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 使用[ElasticSearch](https://www.elastic.co/cn/elasticsearch/)（下文简称ES）搜索服务器存储并检索数据。
- 使用[elasticsearch](https://pypi.org/project/elasticsearch/)库使得Python脚本能调用ES服务。
- 相关软件版本如下：
  - Python 3.6.2
  - ElasticSearch 7.10.0
  - elasticsearch 7.10.0

### 2 获取干员信息数据
直接使用[干员图](https://github.com/Schlampig/OaKnights/tree/main/OperatorGraph)项目中获取到的干员信息数据文件[operator_all.json](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_all.json)。

### 3 获取游戏剧本数据
原始解包数据来自[这里](https://github.com/Dimbreath/ArknightsData)，该课题只用到zh-CN下的数据。运行脚本[clean_data.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/clean_data.py)的方法**parser_all**将主剧情、活动剧情、悖论模拟的对话正文和剧情概述提取、整理再存储至文件[story_raw.json](https://github.com/Schlampig/OaKnights/blob/main/RelateData/story_raw.json)（请留意脚本中原始文件的存放路径，可根据实际情况修改）。

### 4 构建入库数据
运行脚本[prepare_data.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/prepare_data.py)中的**get_operator_info**和**get_story_info**方法分别处理干员信息数据集operator_all.json和游戏剧本数据集story_raw.json。数据格式统一为：
```
entry = [{"person": string, "prefix": string, "content": string}, ...]
```
其中，数据以列表结构存储，列表每一项表示入库的一则词条（或称answer）。每个词条是字典结构，其中person为该词条正文出现的干员名称，prefix为对该词条的描述，content为该词条的正文。例如下面示例的这几个词条：
```
{'content': '12F的出生日期为：3月3日', 'person': '12F', 'prefix': ''}
{'content': '12F在任命助理的语音记录中曾用中文说过：抱歉，我能做的事情很有限，也不太会说话，但作为助理感到很荣幸，如果我能帮到博士阁下那就太好了。', 'person': '12F', 'prefix': ''}
{'content': '12F在交谈1的语音记录中曾用日文说过：ドクター殿。嫌なことはいずれ過ぎ去っていくものです。みなさんはドクター殿を信頼してついてきているのですから、もっと自信をお持ちください。', 'person': '12F', 'prefix': ''}
{'content': '大人们见到这个医疗箱，也会高兴的！', 'person': '孱弱的孩子', 'prefix': '在活动的level_act9d0_st01章节，孱弱的孩子曾说：'}
{'content': '你说是吧。', 'person': 'W', 'prefix': '在活动的level_act9d0_st01章节，W曾说：'}
{'content': '塔露拉。', 'person': 'W', 'prefix': '在活动的level_act9d0_st01章节，W曾说：'}
```
在处理干员基本信息数据时，还使用一个列表lst_person存储下“登场”干员的中文代号。
最终，包含所有词条的entry和干员代号列表lst_person一并存入es_data.json文档，由于这个文档超过25MB，且能快速生成，因而未放在该课题中。

### 5 启动ElasticSearch
在该课题中，ES用于存储上一步构建的待入库词条，并提供高速检索、匹配算法，便于根据用户输入的文本查询入库词条并返回答案。要将es_data.json的数据（也就是entry）存入ES，首先应开启ES服务，步骤如下：
- 下载并解压ES压缩包elasticsearch-7.10.0
- 进入elasticsearch-7.10.0压缩包
```bash
cd elasticsearch-7.10.0
```
- 在压缩包的config路径下，修改配置文件，设置调用ES服务的接口。使用nano或vim指令打开.yml文件，在其中找到**http.port:xxxx**，在其后输入自定义接口号即可：
```bash
nano elasticsearch.yml
```
- 在压缩包的bin路径下启动ES
```bash
./bin/elasticsearch
```
- 附：入库ES的数据起始存放在以下路径，该课题数据量不大，因此使用一个节点存放。进阶内容请查阅ES官网了解：
```bash
cd ./data/nodes/0/indices/具体index名（通常为数字字母序列）
```

### 6 数据入库
在[es.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/es.py)脚本中构建**ES**类，其中的**load**方法用来载入es_data.py内数据，**es_build**方法用于设置ES入库规则并将数据入库（注意在入库规则中设置分词器，便于后续查找）。第一次入库时间较慢，用该代码入库130000词条约需半小时（[提速方案](https://www.easyice.cn/archives/207)与[提速方案](https://blog.csdn.net/weixin_39198406/article/details/82983256)供参考）。查询时，可以通过设置*re_build*参数为False，表示使用当前数据，不需重新入库。

### 7 数据检索
ES使用基于BM25的方案进行全图检索。[es.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/es.py)中的方法**es_search**设定了一套if-else规则：如果用户输入的问题中未检测到干员中文代码，则使用简单的内容查找规则；否则，将查找范围限定在与当前干员相关的内容。最后，方法**run**用于处理用户输入问题（即query）并返回查找的前K个结果（即answer）。

### 8 命令行交互脚本
最后，课题将通过命令行形式与用户交互，即运行程序后，用户输入任意文本（即query）并回车，算法根据用户输入去ES库全文检索找到前K个最符合结果的答案（即answer）反馈回来。[ask.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/ask.py)使用一个循环来保持交互始终进行，若希望终止问答，用户只需输入“所有苦难都结束了”即可。

### 9 开始问答吧
运行[ask.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/ask.py)开始问答体验 :)
```bash
python ask.py
```
注：不在干员名单中的角色无法通过人名限定搜索范围，例如塔露拉、霜星等；对于干员信息的检索，以[干员名]的[属性名]作为输入，可以较精准获取想要的信息（不包含未入库的信息，例如干员间的关系）；对于不包含干员信息的检索，算法更可能从剧本正文中摘录句子返回；由于这只是个伪问答系统，出现答非所问完全正常 > <


## 更新截点
2021年3月9日，干员信息更新至[画中人](http://prts.wiki/w/%E7%94%BB%E4%B8%AD%E4%BA%BA)活动，剧本信息与开发时间点获取的[解包数据](https://github.com/Dimbreath/ArknightsData)同步。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
