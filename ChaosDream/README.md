# 混沌迷梦
*by KuyiKing*

> 这个小课题将使用明日方舟PRTS的干员图像数据和收集自维基百科的开源图像数据，使用神经风格迁移（Neural Style Transfer, NST）和深梦（DeepDream）算法，合成具有不同画风的干员图像。


## 效果

### 使用神经风格迁移的效果（猜猜看都是谁）
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_BeesWax.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Glaucus.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Indigo.jpg" height=45% width=45% /></center>
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_WaaiFu.jpg" height=45% width=45% /></center>
</br>

### 使用深梦（克苏鲁）效果的水月
<center><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_dreamed_Mizuki.jpg" height=45% width=45% /></center>
</br>

### 不同画风的斯卡蒂
<left><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Skadi_1.jpg" height=25% width=25% /></left>
<right><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Skadi_2.jpg" height=25% width=25% /></right>
<left><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Skadi_3.jpg" height=25% width=25% /></left>
<right><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Skadi_4.jpg" height=25% width=25% /></right>
<left><img src="https://github.com/Schlampig/OaKnights/blob/main/ExamplePicture/eg_cd_nst_Skadi_5.jpg" height=25% width=25% /></left>
</br>

## 步骤

### 1 配置环境
- 该课题的全部代码使用[Python](https://www.python.org/)脚本语言编写，在命令行运行。
- 该课题使用深度学习框架[PyTorch](https://pytorch.org/)搭建神经网络模型。
- 该课题使用的神经风格迁移代码非原创，修改自[Aditya Gupta](https://github.com/Adi-iitd)的项目[AI-Art](https://github.com/Adi-iitd/AI-Art).
- 该课题使用的深梦代码非原创，修改自[wmn7](https://github.com/wmn7)的项目[deep-dream-pytorch](https://github.com/wmn7/ML_Practice/blob/master/2019_05_27/deep-dream-pytorch.ipynb)，也参考了[Aleksa Gordić](https://github.com/gordicaleksa)的项目[pytorch-deepdream](https://github.com/gordicaleksa/pytorch-deepdream)。
- 该课题中，神经风格迁移代码需要在GPU环境运行，深梦代码可在GPU或CPU上运行（因为本质上深梦只用到了模型推断，不需要后向传播修改大量网络参数）。
- 主要软件或模型的版本如下：
  - Python 3.6.2
  - PyTorch 1.5.0 与相应版本的 Torchvision 0.2.0
  - Python Imaging Library (PIL) 5.0.0
  - [VGG16](https://download.pytorch.org/models/vgg16-397923af.pth)(在torchvision.models脚本中可以找到各自预训练图像模型的下载地址，也可以尝试vgg19、resent50等模型)

### 2 准备数据
  * 神经风格迁移需要输入内容图像（content_fig）与风格图像（style_fig），最终生成的图像内容来自content_fig，风格则是style_fig的。
  * 深梦需要输入内容图像（content_fig）即可，最终生成的图像内容来自content_fig，风格则来自VGG16（或其他你使用的预训练图像模型）不同激活层提取的特征。
  * 本课题使用来自[明日方舟PRTS](https://prts.wiki/w/%E9%A6%96%E9%A1%B5)的干员立绘图作为content_fig，使用来自[WikiArt](https://www.wikiart.org/)的世界名画作为style_fig。

### 3 文件架构
```
---> dataset ---> content_fig  # 这个目录下放干员图
              |-> style_fig    # 这个目录下放世界名画
 |-> neural_style_transfer.py  # 运行这个脚本，执行神经风格迁移
 |-> deep_dream.py             # 运行这个脚本，执行深梦
```

### 4 运行程序
  * 无论神经风格迁移还是深梦都是训练完成即得到生成的图像。为方便训练，在[neural_style_transfer.py](https://github.com/Schlampig/OaKnights/blob/main/ChaosDream/neural_style_transfer.py)和[deep_dream.py](https://github.com/Schlampig/OaKnights/blob/main/ChaosDream/deep_dream.py)中都写了循环执行函数。
  * 运行后，神经风格迁移脚本会两两结合content_fig与style_fig生成图像：
    ```bash
    python neural_style_transfer.py
    ```
  * 而深梦脚本会逐个处理content_fig图像：
    ```bash
    python neural_style_transfer.py
    ```
  * 嫌麻烦的话，可以在脚本里找单独执行一次的函数来调用即可。生成的图像都在当前目录下存放。

### 5 学习材料
  * [AI-Art](https://github.com/Adi-iitd/AI-Art): about PyTorch (and PyTorch Lightning) implementation of Neural Style Transfer, Pix2Pix, CycleGAN, and Deep Dream.
  * [deepdream](https://github.com/google/deepdream) and its various approaches/tutorials: [pytorch-deepdream](https://github.com/gordicaleksa/pytorch-deepdream), [neural-dream](https://github.com/ProGamerGov/neural-dream), [deep-dream-pytorch](https://github.com/wmn7/ML_Practice/blob/master/2019_05_27/deep-dream-pytorch.ipynb).

## 更新截点
2022年2月7日，干员信息更新至[将进酒](https://prts.wiki/w/%E5%B0%86%E8%BF%9B%E9%85%92)活动。


## 注意
- 该课题仅供爱好者学习、交流，禁止商用！
- 转载请注明原作者，并附出处链接。

---
