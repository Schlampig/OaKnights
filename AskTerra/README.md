# 问泰拉
*by KuyiKing*

> 这个小课题将干员信息与游戏剧本数据整理入库，使用简单的全文检索服务，根据用户输入问题，反馈库中匹配到的答案，实现伪问答系统。


## 效果

### 提问干员信息
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/xxx.png" height=35% width=35% /></center>

### 查找剧本内容
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/xxx.png" height=35% width=35% /></center>

## 步骤
注：如果想直接体验问答内容，可以从[第x步](#quick_link)看起，前面的数据均可在[RelateData](https://github.com/Schlampig/OaKnights/tree/main/RelateData)路径下获取。

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 使用[ElasticSearch](https://www.elastic.co/cn/elasticsearch/)搜索服务器存储并检索数据。
- 相关软件版本如下：
  - Python 3.6.2
  - ElasticSearch 7.10.0

### 2 获取干员信息数据
直接使用[干员图](https://github.com/Schlampig/OaKnights/tree/main/OperatorGraph)项目中获取到的干员信息数据文件[operator_all.json](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_all.json)。

### 3 获取游戏剧本数据
原始解包数据来自[这里](https://github.com/Dimbreath/ArknightsData)，该课题只用到zh-CN下的数据。运行脚本[clean_data.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/clean_data.py)的方法**parser_all**将主剧情、活动剧情、悖论模拟的对话正文和剧情概述提取、整理再存储至文件[story_raw.json](https://github.com/Schlampig/OaKnights/blob/main/RelateData/story_raw.json)（请留意脚本中原始文件的存放路径，可根据实际情况修改）。

### 4 构建入库数据
运行脚本[prepare_data.py](https://github.com/Schlampig/OaKnights/blob/main/AskTerra/prepare_data.py)中的**get_operator_info**和**get_story_info**分别处理干员信息数据集operator_all.json和游戏剧本数据集story_raw.json。数据格式统一为：
```
data_all = [{"person": string, "prefix": string, "content": string}, ...]
```
其中，person为该

### 5 数据入库
。

### 6 生成干员信息三元组
根据方舟干员图谱关系三元组列表及operator_all.json中的所有干员信息，使用脚本[build_operator_net.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/build_operator_net.py)中的**get_entity_and_relation**方法，将这些结构化信息转化为两张新的.csv格式表格：干员关系三元组表[operator_relation.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_relation.csv)和干员实体三元组表[operator_entity.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_entity.csv)。

### 7 新增干员人际关系图谱
等等，我们似乎遗漏了一个非常重要但在Wiki里没有的干员信息，那就是干员之间的人际关系。这个关系的难点在于，并非静态，而且对于不同玩家，心中承认的关系也各不相同。于是我们单独建立一张[CP表](https://github.com/Schlampig/OaKnights/blob/main/OperatorSchema/operator_cp.xlsx)，并利用脚本[add_operator_relation.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/add_operator_relation.py)将这张表中的内容补充到operator_relation.csv中，得到完整的干员关系三元组表[operator_relation_cp.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_relation_cp.csv)。此处CP表中只列出了很少的一部分关系（大部分遵从游戏原设），为了使泰拉大陆的人们联系得更紧密，欢迎大家在[Issue](https://github.com/Schlampig/OaKnights/issues/1)中留言补充干员关系，随着版本迭代，会选取新关系加入。

### <span id="quick_link">8 生成干员可视化网络</span>
将operator_entity.csv与operator_relation_cp.csv（如果你不想加入干员关系，也可以使用operator_relation.csv）导入Neo4j库中。导入流程如下：
- 解压Neo4j压缩包
- 进入Neo4j压缩包
- 清空压缩包中原本的图谱（也可以设置添加新图谱，这里为求简单直接删除原图谱），**注意rm算法的用法**。
```bash
cd data/databases/graph.db/
rm -rf *
```
- 进入/bin路径下
```bash
cd ../../../bin/
```
- 导入两个.csv文件
```bash
./neo4j-import -into /your_path/neo4j-community-3.5.5/data/databases/graph.db/ --nodes /Users/schwein/neo4j-data/operator_entity.csv --relationships /Users/schwein/neo4j-data/operator_relation_cp.csv --ignore-duplicate-nodes=true --ignore-missing-nodes=true
```
- 导入成功

### 9 启动图谱，查询自己感兴趣的内容
- 在/bin路径下启动图谱：
```bash
./neo4j console
```
- 启动顺利的话，会看见命令行出现形如下示的一句话：
```bash
INFO  Remote interface available at http://localhost:7474/
```
- 在浏览器中打开http://localhost:7474/
- 第一次可能需要设置密码，按喜好来就好。
- 将脚本[add_operator_relation.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/add_operator_relation.py)中生成的示例查询语句复制粘贴到界面代码框中，运行即可。
- 尝试更改查询语句，查看不同的匹配结果。
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_05.png" height=50% width=50% /></center>


## 更新截点
2021年2月18日，干员信息更新至[画中人](http://prts.wiki/w/%E7%94%BB%E4%B8%AD%E4%BA%BA)活动。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
