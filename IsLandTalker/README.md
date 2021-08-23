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

### 2 准备预训练语言模型
下载[中文版本UniLM](https://github.com/YunwenTechnology/Unilm)，里面包含三个文件：**vocab.txt**为词表，请将其中的\[unused99]改写为\[END]，即使用\[END]作为生成句子终止的标识符；**config.json**为该语言模型的配置信息，不作任何更改；**pytorch_model.bin**为中文UniLM模型文件，该模型是在1.4.0版PyTorch与2.6.0版Transformers下训练的，如果直接用现在的1.2.0版PyTorch读取，由于低版本框架读取高版本模型的缘故会报错。解决方法是，在高版本的PyTorch库中读取该模型、转存为pickle文件，再在低版本的实际运行环境里读取pickle文件即可：

- 在1.4.0版PyTorch下读取、存储
  ```
  import torch
  import pickle

  state_dict = torch.load("pytroch_model.bin", map_location=torch.device("cpu"))
  with open("unilm.pth", "wb") as f:
      pickle.dump(state_dict, f)
  ```
- 在1.2.0版PyTorch下读取
  ```
  try:
      state_dict = torch.load(init_checkpoint, map_location='cpu')
  except:
      with open(init_checkpoint, "rb") as f:
          state_dict = pickle.load(f)
  ```
最后，把**vocab.txt**、**config.json**、**unilm.pth**三个文件放在[**check_points**](https://github.com/Schlampig/OaKnights/tree/main/IsLandTalker/check_points)路径下。
  
### 3 准备数据

### 4 文件架构
```
-> bert_codes -> __init__.py
             |-> modeling.py: BERT与UniLM模型核心代码
             |-> optimization.py: 优化算法相关代码
             |-> tokenization.py: 分词策略相关代码
             |-> utils.py: 其他辅助代码，包括文件读取、文本处理、文件储存等
  |-> check_points -> 生成的新模型文件、该模型的配置文件、训练过程日志文件将放在这里
  |-> data -> story_train.json & story_dev.json: 清洗后的原始文本
          |-> fea_story_train.json & fea_story_dev.json: 经过oak_train.py预处理后生成的、用于训练与验证的数据集
  |-> pretrained_model -> unilm_1.2 -> 上文第2步中得到的语言模型文件、语言模型配置文件、语言模型相关词表放在这里
  |-> oak_train.py: 训练脚本，运行该脚本后，读取pretrained_model下的现有语言模型、生成check_points下的新语言模型
  |-> oak_predict.py: 预测脚本，运行该脚本后，读取check_points下的新语言模型
  |-> ask.py: 最终运行的脚本，调用oak_predict.py
```

### 5 训练新语言模型

### 6 运行程序



## 更新截点
2021年5月1日，干员信息更新至[覆潮之下](http://prts.wiki/w/%E8%A6%86%E6%BD%AE%E4%B9%8B%E4%B8%8B)活动，剧本信息与开发时间点获取的[解包数据](https://github.com/Dimbreath/ArknightsData)同步。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
