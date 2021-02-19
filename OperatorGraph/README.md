# 干员图

> 这个小课题将来自[明日方舟中文Wiki](http://prts.wiki/w/%E9%A6%96%E9%A1%B5)的干员数据可视化，以图谱形式呈现，并可对生成的图谱进行一些点与边的查询操作。

---

## 效果

### 查看干员“刻刀”的所有信息
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_1.png" height=50% width=50% />

### 找出不同星座的代表干员？
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_2.png" height=50% width=50% />

### 哪些干员的种族是萨卡兹？
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_3.png" height=50% width=50% />

### 干员“温蒂”与干员“初雪”的人际关联是？
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_4.png" height=50% width=50% />

### 俯瞰泰拉大陆全势力图谱
<img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_og_0.png" height=50% width=50% />

---
## 步骤

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 解析网络文件时使用了[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)库。
- 使用[Neo4j](https://neo4j.com/)图数据库展示最终的网络。
- 相关库的版本如下：
  - TODO


### 2 获取干员名单
运行脚本[get_operator_info.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/get_operator_info.py)的方法**crawl_list_page**将[干员一览](http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88)页面爬取下来；接着，使用方法**parser_list_page**解析该页面，获得干员代号清单。注意，原始的干员一览页面仅显示前50名干员，此处应在下拉列表选择“每页显示500干员”，这样就能一次处理完毕。等游戏干员总数超过500时，我们再更新脚本。

### 3 设计干员信息导图
想要获取干员的哪些基本信息呢？虽说多多益善，但凭空想象难以周全，我们使用[xmind](https://www.xmind.cn/)软件绘制一个[方舟干员信息导图](https://github.com/Schlampig/OaKnights/blob/main/OperatorSchema/%E6%96%B9%E8%88%9F%E5%B9%B2%E5%91%98%E4%BF%A1%E6%81%AF%E5%AF%BC%E5%9B%BE_20210208.png)，将计划提取的每个干员的信息列出来。

### 4 获取干员基本信息
以干员“温蒂”为例，运行脚本[get_operator_info.py](https://github.com/Schlampig/OaKnights/blob/main/OperatorGraph/get_operator_info.py)的方法**crawl_operator_info**下载干员的[可编辑页面](http://prts.wiki/index.php?title=%E6%B8%A9%E8%92%82&action=edit)，**crawl_operator_voice**方法下载干员的[语音文本页面](http://prts.wiki/w/%E6%B8%A9%E8%92%82/%E8%AF%AD%E9%9F%B3%E8%AE%B0%E5%BD%95)；接着，使用**parser_operator_info**和**parser_operator_voice**方法分别对这两个页面的内容进行提取；为方便处理，使用**check_single_operator**直接调用以上两个方法获得温蒂干员的所有信息；为一次获取所有干员的信息，结合在第2步获得的干员清单，使用**check_all_operator**方法批量处理所有干员信息；最后，所有获得的干员信息以.json格式存储在名为[operator_all.json](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_all.json)的文档中。为了方便查看运行效果，可以使用**json2csv**方法将operator_all.json转换为表格文档[operator_all.csv](https://github.com/Schlampig/OaKnights/blob/main/RelateData/operator_all.csv)。

### 5 设计干员关系三元组图谱（该使用哪些关系连接干员）
这是正文

### 6 将干员信息转存为实体与关系，存放在csv文件中
这是正文

### 7 新增干员人际关系图谱（开issue补充cp）
这是正文

### 8 将文件导入neo4j图谱
这是正文

### 9 使用图谱的查询语句，查询感兴趣的内容
这是正文

---
## 更新截点
更新至画中人活动
