# 新闻人物言论自动提取

目标

- 输入: 一段新闻文本(Text)
- 输出: 文中每个人物/实体的观点(List)
## 快速上手

安装说明 [INSTANLL.md](./INSTALL.md) 


## 1. 数据层

能够使用数据库操作，对数据库中的信息进行访问

### 获取数据

本项目使用两个数据源，一个是wiki语料库，一个是新闻语料库。

- wiki语料库已经在作业四中使用过了

- 新闻语料库

  - 可以从sql中提取
  - 可以从百度网盘自己下载

**从SQL中获取需要用到以下内容** 

1. 数据库为云数据库，配置为 Mysql; 请⼤家下载 DataGrip 或者 MySQL WorkBench 进⾏数据库的访问;

2. 用户名：

3. 用户密码：

4. 数据库名：

5. 如果在 DataGrip 下配置，则配置的界⾯见项目一指导


## 2. 模型层

构建自然语言处理模型，能够提取出文章中客户的言论
###  1. 使用wiki中文语料和新闻语料训练word2vector

- 使用维基百科下载中文语料库
- 从下载的语料库中抽取维基百科的内容，将其保存在txt文件中
- 维基百科中的内容有的是繁体字，需要将其转换成简体字，推荐使用[hanziconv](https://pypi.org/project/hanziconv/)一行代码搞定
- 使用jieba进行切词，然后存进新的文件中
- 用Gensim的`LineSentenc`类读取含有切分好的单词的txt文件，训练成词向量Model


###  2. 使用词向量模型 生成与"说"相近的词语
1. 在基于**第⼀课，第⼆课讲过的搜索树** + **第四课的动态规划**，结合**第五课**所讲的内容，

 - 第二课：广度优先遍历，深度优先遍历
 - 第四课：动态规划------**递归的暴力解法 -> 带备忘录的递归解法 -> 非递归的动态规划解法**
 - 第五课: 
   -  NER
   - Dependency Parsing
   - TF-IDF
2. 获得所有与“说”意思接近的单词：`result = pd.Series(model.most_similar(u'保利')) `

3. 思考：词向量结合图搜索的时候，每个找到的单词如何赋其权重，这个和⼴度优先，A*搜索有何异同？


### 3. 确定言论的结束

要确定言论的结束，最简单的方式是碰见句号的时候就停止，但是有的言论可能是跨了多个句号，那么此时如何确定言论的结束，就是一个比较 tricky 的问题。 解决方法是：**把判断两句话是不是类似的、是不是说的同一个主题这个问题变成这两个句子的距离是不是小于某个阈值，方法就是使用向量进行对比** 

要获得句子的向量，一种方法是使用 Tf-idf  进行句子向量化。 Tf-idf 这是一种比较基础的向量化方式， 但是不能判断不相同的单词的语义相似性。

#### 3.1 基于SIF方法计算句子相似度，来判断句子结束

在词向量提出来之后，有一个比较好的方式就是基于词向量进行句子的向量化，普林斯顿在2017 年提出来一个方法：SIF，原理是使用单词的词向量加权 + PCA 降维  

- 作为一种**无监督**计算句子之间相似度的方法, **sif sentence embedding**使用预训练好的词向量, 使用加权平均的方法, 对句子中所有词对应的词向量进行计算, 得到整个句子的embedding向量. 再使用句子向量进行相似度的计算

​       基本思路是：给定上下文中，一个词的出现概率由上下文和作为平滑项的词频决定, 算法内容如下：

​       **输入**： 
​       预训练的词向量 ${v_w:w∈V}$，例如`word2vec、glove`等 

​       待处理的句子集合 $S$

​       参数$a$（论文中建议$a$的范围：$[1e−4,1e−3]$）

​       词频估计 ${p(w):w∈V}$

​       **输出**： 
​       句子向量${v_s:s∈S}$

​       算法的关键两步如下

​     ![1567387204871](F:\ML\Deep Learning\NLP\Course\2019-summer\p1\1567387204871.png) 

- 第一步：计算向量表示的平均值，每个单词都有一个独立的权重，权重为常数α除以α与单词频率的和。    这样的话可以使高频词的权重较小。 
- 第二步：针对所有句子组成的句子表示矩阵，计算每个句子表示的第一主成分，然后减去在第一主成分上的投影。 类似PCA：使用sklearn中的`TruncatedSVD`计算每个句子表示的第一主成分

参考：

1. https://www.cnblogs.com/databingo/p/9788244.html
2. https://blog.csdn.net/sinat_31188625/article/details/72677088#commentsedit
3. https://blog.csdn.net/yxiachan/article/details/81292902
4. https://github.com/PrincetonML/SIF

#### 3.2 基于rnn判断一句话能否作为人说的话，来判断句子结束

使用双向循环神经网络模型，在这个模型中，

- 首先，每个词通过嵌入层得到**特征向量**。
- 然后，使用双向循环神经网络对特征序列进一步编码得到**序列信息**。
- 最后，将编码的序列信息通过**全连接层**变换为输出。具体来说，
  - 我们可以将双向长短期记忆在最初时间步和最终时间步的隐藏状态连结，
  - 作为特征序列的表征传递给输出层分类。
- 在实现的`BiRNN`类中，
  - `Embedding`实例即嵌入层
  - `LSTM`实例即为序列编码的隐藏层
  - `Dense`实例即生成分类结果的输出层。

#### 3.3 综合句子相似度和rnn模型判断

- rnn判断结果为True则直接返回
- rnn判断结果为False且可信度大于阈值则返回False
- rnn判断结果为False且可信度小于阈值则根据相似度判断

## 3.视图层

使用 HTML，Python Web 服务进行网页展示

技术栈：Flask+ Bootstrap + HTML（+D3）

## 4.参考

- [flask文档](https://dormousehole.readthedocs.io/en/latest/) 
- [pyhanlp](https://github.com/hankcs/pyhanlp) 
- [hanlp在线演示](http://hanlp.com/) 
- [普林斯顿句子向量论文](https://openreview.net/forum?id=SyK00v5xx) 
- [论文代码](https://github.com/PrincetonML/SIF) 
- [论文解读](https://blog.csdn.net/sinat_31188625/article/details/72677088#commentsedit) 
- [解读代码](https://github.com/jx00109/sentence2vec/blob/master/s2v-python3.py) 
- [云浮科技句法分析](https://www.yunfutech.com/demo?tab=1) 
- [Scikit-learning TF-IDF句子向量化](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) 



