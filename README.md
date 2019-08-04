# 新闻人物言论自动提取

# 1. 数据层

能够使用数据库操作，对数据库中的信息进行访问

## 1. 获取数据



1. 数据库为云数据库，配置为 Mysql; 请⼤家下载 DataGrip 或者 MySQL WorkBench 进⾏数据库的访问;

2. 用户名：

3. 用户密码：

4. 数据库名：

5. 如果在 DataGrip 下配置，则配置的界⾯
   如图:

   ![1564927574522](C:\Users\baideqian\AppData\Roaming\Typora\typora-user-images\1564927574522.png)

# 2. 模型层

构建自然语言处理模型，能够提取出文章中客户的言论
## 2.  获得所有表示“说”的意思的单词

   1. 使⽤维基百科+新闻语料库制作的词向量，在基于**第⼀课，第⼆课讲过的搜索树** + **第四课的动态规划**，结合**第五课**所讲的内容，获得出所有与“说”意思接近的单词
   2.  思考：词向量结合图搜索的时候，每个找到的单词如何赋其权重，这个和⼴度优先，A*搜索有何异同？

   ## 3. 使用 NER，Dependency Parsing等对句子形式进行解析

   1. 使⽤ NER，Dependency Parsing 等⽅式，获得是谁说了话，说了什么话。其中 Dependency Parsing 我们有Stanford 的 CoreNLP 和哈⼯⼤的LTP，这两个⼯具的安装过程会⽐较⿇烦，⼤家要做好⼼理准备。

      建议使用哈工大的： LTP: https://github.com/HIT-SCIR/pyltp



## 4. 确定言论的结束

1. 在确定了谁说的，说了什么之后，我们要做的就是确定这个话语的结束。
   要确定这个话语如何结束
2. 这里给大家推荐一个简单性 和高效性两者比较平衡的方法，其原理就是使用单词的词向量加权 + PCA 降维 这个方法是 普林斯顿大学2017 年提出来的一个方法，很简单，但是效果也不错。
   - 普林斯顿句⼦向量原始论⽂ Paper:https://openreview.net/pdf?id=SyK00v5xx
   - Scikit-learning TFIDF句句⼦子向量量化: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html



# 3.视图层

使用 HTML，Python Web 服务进行网页展示
