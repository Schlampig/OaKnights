# 干员图
*by KuyiKing*

> 这个小课题将来自[明日方舟中文Wiki](http://prts.wiki/w/%E9%A6%96%E9%A1%B5)的干员数据可视化，以图谱形式呈现，并可对生成的图谱进行一些点与边的查询操作。


## 效果

### 查看干员“刻刀”的所有信息
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_01.png" height=50% width=50% />

### 找出不同星座的代表干员？
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_02.png" height=50% width=50% />

### 哪些干员的种族是萨卡兹？
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_03.png" height=50% width=50% />

### 干员“温蒂”与干员“初雪”的人际关联是？
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_04.png" height=50% width=50% />

### 俯瞰泰拉大陆全势力图谱
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_00.png" height=50% width=50% />


## 步骤

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 解析网络文件时使用了[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)库。
- 使用[Neo4j](https://neo4j.com/)图数据库展示最终的网络。
- 相关软件版本如下：
  - Python 3.6.2
  - Neo4j 3.5.5(community)
  - BeautifulSoup4 4.5.3

### 2 获取干员名单
运行脚本[get_operator_info.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/get_operator_info.py)的方法**crawl_list_page**将[干员一览](http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88)页面爬取下来；接着，使用方法**parser_list_page**解析该页面，获得干员代号清单。注意，原始的干员一览页面仅显示前50名干员，此处应在下拉列表选择“每页显示500干员”，这样就能一次处理完毕。等游戏干员总数超过500时，我们再更新脚本。

### 3 设计干员信息导图
想要获取干员的哪些基本信息呢？虽说多多益善，但凭空想象难以周全，我们使用[xmind](https://www.xmind.cn/)软件绘制一个[方舟干员信息导图](https://github.com/Schlampig/OaKnights/blob/main/OperatorSchema/%E6%96%B9%E8%88%9F%E5%B9%B2%E5%91%98%E4%BF%A1%E6%81%AF%E5%AF%BC%E5%9B%BE_20210208.png)，将计划提取的每个干员的信息列出来。

### 4 获取干员基本信息
以干员“温蒂”为例，运行脚本[get_operator_info.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/get_operator_info.py)的方法**crawl_operator_info**下载干员的[可编辑页面](http://prts.wiki/index.php?title=%E6%B8%A9%E8%92%82&action=edit)，**crawl_operator_voice**方法下载干员的[语音文本页面](http://prts.wiki/w/%E6%B8%A9%E8%92%82/%E8%AF%AD%E9%9F%B3%E8%AE%B0%E5%BD%95)；接着，使用**parser_operator_info**和**parser_operator_voice**方法分别对这两个页面的内容进行提取；为方便处理，使用**check_single_operator**直接调用以上两个方法获得温蒂干员的所有信息；为一次获取所有干员的信息，结合在第2步获得的干员清单，使用**check_all_operator**方法批量处理所有干员信息；最后，所有获得的干员信息以.json格式存储在名为[operator_all.json](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_all.json)的文档中。为了方便查看运行效果，可以使用**json2csv**方法将operator_all.json转换为表格文档[operator_all.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_all.csv)。

### 5 设计干员图谱关系三元组列表（该使用哪些关系连接干员）
虽然得到干员信息，但要构建一个全面的干员网络，需要知道干员之间的信息是如何连接的。知识图谱中采用实体与关系来表示结构化信息，对应为网络的节点与边。在绘制图谱之前，我们使用三元组来定义好需要用到的实体类型与关系类型。一个三元组的结构为(头实体，关系，尾实体)，表示头实体->关系->尾实体。将这样的三元组罗列出，得到[方舟干员图谱关系三元组列表](https://github.com/Schlampig/OaKnights/blob/main/OperatorSchema/%E6%96%B9%E8%88%9F%E5%B9%B2%E5%91%98%E5%9B%BE%E8%B0%B1%E5%85%B3%E7%B3%BB%E4%B8%89%E5%85%83%E7%BB%84%E5%88%97%E8%A1%A8_20210218.xlsx)。

### 6 生成干员信息三元组
根据方舟干员图谱关系三元组列表及operator_all.json中的所有干员信息，使用脚本[build_operator_net.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/build_operator_net.py)中的**get_entity_and_relation**方法，将这些结构化信息转化为两张新的.csv格式表格：干员关系三元组表[operator_relation.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_relation.csv)和干员实体三元组表[operator_entity.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_entity.csv)。

### 7 新增干员人际关系图谱
等等，我们似乎遗漏了一个非常重要但在Wiki里没有的干员信息，那就是干员之间的人际关系。这个关系的难点在于，并非静态，而且对于不同玩家，心中承认的关系也各不相同。于是我们单独建立一张[CP表](https://github.com/Schlampig/OaKnights/blob/main/OperatorSchema/operator_cp.xlsx)，并利用脚本[add_operator_relation.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/add_operator_relation.py)将这张表中的内容补充到operator_relation.csv中，得到完整的干员关系三元组表[operator_relation_cp.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_relation_cp.csv)。此处CP表中只列出了很少的一部分关系（大部分遵从游戏原设），为了使泰拉大陆的人们联系得更紧密，欢迎大家在[Issue](https://github.com/Schlampig/OaKnights/issues/1)中留言补充干员关系，随着版本迭代，会选取新关系加入。

### 8 生成干员可视化网络
将operator_entity.csv与operator_relation_cp.csv（如果你不想加入干员关系，也可以使用operator_relation.csv）导入Neo4j库中。导入流程如下：
- 解压neo4j压缩包
- 进入neo4j压缩包
- 清空压缩包中原本的图谱（也可以设置添加新图谱，这里为求简单直接删除原图谱），注意rm算法用法。
```bash
cd data/databases/graph.db/
rm -rf *
```
- 进入bin路径下
```bash
cd ../../../bin/
```
- 导入两个.csv文件
```bash
./neo4j-import -into /your_path/neo4j-community-3.5.5/data/databases/graph.db/ --nodes /Users/schwein/neo4j-data/operator_entity.csv --relationships /Users/schwein/neo4j-data/operator_relation_cp.csv --ignore-duplicate-nodes=true --ignore-missing-nodes=true
```
- 导入成功

### 9 启动图谱，查询自己感兴趣的内容
- 在bin文件中，启动图谱：
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
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_05.png" height=50% width=50% />


## 更新截点
2021年2月18日，干员信息更新至[画中人](http://prts.wiki/w/%E7%94%BB%E4%B8%AD%E4%BA%BA)活动。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
