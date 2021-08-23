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
:sweat_smile:为什么不直接在1.4.0甚至更高版本的PyTorch下完成整个模型的训练、运行呢？问得好，因为PyTorch安装得很早，因为懒没升级，所以……有兴趣的朋友不妨试试（应该不会报错，大概吧……）
  
### 3 准备数据
  - 使用[prepro_data.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/prepro_data.py)预处理下载自[解包数据](https://github.com/Dimbreath/ArknightsData)的原始剧情数据，生成[训练文本](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/data/story_train.json)与[验证文本](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/data/story_dev.json)，放到[data](https://github.com/Schlampig/OaKnights/tree/main/IsLandTalker/data)路径下即可。
  - 第一遍运行[oak_train.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/oak_train.py)时,**data2fea**方法会将清洗后的[训练文本](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/data/story_train.json)与[验证文本](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/data/story_dev.json)转换为适合训练UniLM模型的训练集**fea_story_train.json**与测试集**fea_story_dev.json**放在[**data**](https://github.com/Schlampig/OaKnights/tree/main/IsLandTalker/data)路径下。之后再运行时，**data2fea**方法会先检查是否已有**fea_story_train.json**与**fea_story_dev.json**，只有在检测不到时才会重新生成数据集。

### 4 文件架构
将第2步与第3步得到的所有文件放在相应位置后，文件架构如下，可以开始训练模型了（[prepro_data.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/prepro_data.py)严格来说只是数据清洗，不属于训练的文件架构，因此未列出）。
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
在这个任务中，输入的形式为：*[CLS]已知文本[SEP]生成文本[END]*。运行[oak_train.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/oak_train.py)：
```bash
python oak_train.py
```
训练完毕后，会在[pretrained_model/unilm_1.2](https://github.com/Schlampig/OaKnights/tree/main/IsLandTalker/pretrained_model/unilm_1.2)路径下生成名为**islandtalker_model**的新模型文件（可以理解为，经过训练，原本的**unilm.pth**内相关参数得到更新，使得新的模型更适合方舟风格的台词）。另外，还会在同一个路径下生成训练参数信息文件**setting.txt**和训练日志文件**log.txt**。在与[oak_train.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/oak_train.py)同层目录下还会得到**log_result_now_epoch.txt**，用以记录最近一次跑验证集的结果。训练时长供参考：V100服务器4GPU，50个Epoch大约跑6小时，其实用不着这么多Epoch，一般15个Epoch就能得到比较通顺的句子了。

### 6 运行程序
当运行[ask.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/ask.py)时，程序会首先调用[oak_predict.py](https://github.com/Schlampig/OaKnights/blob/main/IsLandTalker/oak_predict.py)，后者实际就是载入新模型**islandtalker_model**并等待输入文本进行处理。
```bash
python ask.py
```
目前设计为可以不断提问、回答，若想结束，请输入“我问完了”。

### Tips
  - 为使生成效果更好，可以自行收集大量轻小说、文字冒险游戏的文本，先预精调（pre-finetune）一遍，再代入方舟文本精调（finetune）。截图中的效果正式采用这种方法得到的（可惜模型文件由于一些原因无法开源）。直接使用上述简化步骤所得模型效果较有限。事实上，这种预先让语言模型“适应”问题域或任务类型的方法有不少研究进展，可参考博客[Recent Advances in Language Model Fine-tuning](https://ruder.io/recent-advances-lm-fine-tuning/)([中文概述版](https://mp.weixin.qq.com/s/XVZSAxaWM30t9rOeXYM03A))。
  - 数据质量对模型效果至关重要，由于方舟文本特色，建议针对大量省略号、括号、感叹号、问号、拟声词、空白等作处理。
  - 尽量使得上下文长度适宜。
  - 在解码阶段，这里使用了贪婪策略（每次取词典里概率最大的那个符号作为当前的输出结果），实际上有许多更经典的策略，比如BeamSearch(集束搜索)及相关变体，感兴趣可以查询并实践。
  - 感兴趣可以尝试其他生成模型，例如[BART](https://huggingface.co/transformers/model_doc/bart.html)、[GPT-2](https://huggingface.co/transformers/model_doc/gpt2.html)、[T5](https://huggingface.co/transformers/model_doc/t5.html)等。


## 更新截点
2021年5月1日，干员信息更新至[覆潮之下](http://prts.wiki/w/%E8%A6%86%E6%BD%AE%E4%B9%8B%E4%B8%8B)活动，剧本信息与开发时间点获取的[解包数据](https://github.com/Dimbreath/ArknightsData)同步。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
