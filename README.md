# 新闻人物言论自动提取
## 线上地址：http://47.105.82.234/
- flask文档：https://dormousehole.readthedocs.io/en/latest/
## 基础目标
- 输入: 一段新闻文本(Text)
- 输出: 文中每个⼈人物/实体的观点(List)
## 挑战目标
基于实体观点，构建实体观点图谱并可视化


# 1. 数据层

能够使用数据库操作，对数据库中的信息进行访问

## 1. 获取数据

本项目使用两个数据源，一个是wiki语料库，一个是新闻语料库。

- wiki语料库已经在作业四中使用过了

- 新闻语料库

  - 可以从sql中提取
  - 可以从百度网盘自己下载，后期应该会有人发网盘链接

  

  **从SQL中获取需要用到以下内容**

1. 数据库为云数据库，配置为 Mysql; 请⼤家下载 DataGrip 或者 MySQL WorkBench 进⾏数据库的访问;

2. 用户名：

3. 用户密码：

4. 数据库名：

5. 如果在 DataGrip 下配置，则配置的界⾯见项目一指导


# 2. 模型层

构建自然语言处理模型，能够提取出文章中客户的言论
## 2.1 获得所有表示“说”的意思的单词

### 2.1.1 使用维基百科+新闻语料库制作词向量

 - 数据读取

 - 繁转简

 - 切词

 - 模型训练

 - 性能测试


### 2.1.2 生成与"说"相近的词语
1. 在基于**第⼀课，第⼆课讲过的搜索树** + **第四课的动态规划**，结合**第五课**所讲的内容，

 - 第一课：
 - 第二课：广度优先遍历，深度优先遍历
 - 第四课：动态规划------**递归的暴力解法 -> 带备忘录的递归解法 -> 非递归的动态规划解法**
 - 第五课: 
   -  NER
   - Dependency Parsing
   - TF-IDF
3. 获得所有与“说”意思接近的单词：`result = pd.Series(model.most_similar(u'保利')) `
4. 思考：词向量结合图搜索的时候，每个找到的单词如何赋其权重，这个和⼴度优先，A*搜索有何异同？

## 3. 使用 NER，Dependency Parsing等对句子形式进行解析

### 3.1 安装工具

使⽤ NER，Dependency Parsing 等⽅式，获得是谁说了话，说了什么话。其中 Dependency Parsing 我们有Stanford 的 CoreNLP 和哈⼯⼤的LTP，这两个⼯具的安装过程会⽐较⿇烦，⼤家要做好⼼理准备。

建议使用哈工大的： LTP: https://github.com/HIT-SCIR/pyltp

### 3.2  句子形式进行解析

1. 判断该句子的中心词 是否为 ”说“的相近词

2. 寻找中心词对应的命名实体

3. 提取 判别标志，如 ， 。 ！ …等作为分句的标志


## 4. 确定言论的结束

### 4.1 目标

1. 在确定了谁说的，说了什么之后，我们要做的就是确定这个话语的结束。要确定这个话语如何结束，这里给大家推荐一个简单性 和高效性两者比较平衡的方法，其原理就是使用单词的词向量加权 + PCA 降维 这个方法是 普林斯顿大学2017 年提出来的一个方法，很简单，但是效果也不错。
   - 普林斯顿句⼦向量原始论⽂ Paper:https://openreview.net/pdf?id=SyK00v5xx
   - Scikit-learning TF-IDF句子向量化: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html


### 4.2 方法
1. 使用词向量加权 / PCA 降维的方式 计算 句子向量
2. 计算 第二个及之后的 句子向量 与 第一个句子向量的 **余弦值**
3.  判断句子之间的相似度 ，低于 0.5 则 判定为 结束

# 3.视图层

使用 HTML，Python Web 服务进行网页展示



# 4.参考

1. https://github.com/MosBest/Automatic-speech-extraction
2. https://github.com/zhengzhihust/news_extraction
