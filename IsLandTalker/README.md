# 岛聊
*by KuyiKing*

> 这个小课题将使用明日方舟剧情的对话数据，并基于UniLM预训练生成语言模型，以训练一个新模型，该新模型能根据用户输入的文本内容，自动生成答复。与[问泰拉（AskTerra）](https://github.com/Schlampig/OaKnights/tree/main/AskTerra)不同，这里返回的答复完全由模型自动生成，而非去底层数据库中搜索、匹配并返回原文。一些意想不到的答复可能会颇具趣味，也可能徒增悲伤。


## 效果
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_00.jpeg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_01.jpeg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_02.jpeg" height=45% width=45% /></center>
</br>

<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_03.jpeg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_04.jpeg" height=25% width=25% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_05.jpeg" height=25% width=25% /></center>
</br>

<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_06.jpeg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_07.jpeg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_it_08.jpeg" height=45% width=45% /></center>

## 步骤

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 该课题使用深度学习框架[PyTorch](https://pytorch.org/)搭建神经网络模型。
- 该课题使用的预训练语言模型为[UniLM](https://github.com/microsoft/unilm/tree/master/unilm)，最初由**微软**提出；该课题使用的是由**云问科技**开源的[中文版本](https://github.com/YunwenTechnology/Unilm)。
- 该课题使用的BERT及UniLM相关脚本参考自[Transformers](https://github.com/huggingface/transformers)与[bert_cn_finetune](https://github.com/ewrfcas/bert_cn_finetune).
- 建议感兴趣的朋友首先了解深度学习、自然语言处理、自然语言生成任务等相关方面的知识。
- 该课题代码需要在GPU环境运行。
- 主要软件或模型的版本如下：
  - Python 3.6.2
  - PyTorch 1.2.0
  - UniLM (在PyTorch=1.4.0与Transformers=2.6.0训练出的模型，要想在PyTorch=1.2.0上跑起来只需要另存为pickle文件再读入就好，详见下文)

### 2 

### 3



## 更新截点
2021年5月1日，干员信息更新至[覆潮之下](http://prts.wiki/w/%E8%A6%86%E6%BD%AE%E4%B9%8B%E4%B8%8B)活动，剧本信息与开发时间点获取的[解包数据](https://github.com/Dimbreath/ArknightsData)同步。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
