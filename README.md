# 自然语言处理项目

#### 安装说明： [INSTANLL.md](./INSTALL.md)

## 新闻人物言论自动提取
程序入口：extract_router.py

解决思路：
1. 使用wiki中文和搜狗新闻语料库训练词向量
2. 使用pagerank算法找出与说相近的词
3. 使用实体分析和句子依存分析找到言论的第一句话
4. 确定言论结束综合了句子相似度和判断一句话是否可以作为人说的话两种方式。
- 句子相似度使用了普林斯顿句子向量论文(https://openreview.net/forum?id=SyK00v5xx)的方法
- 判断一句话是否可以作为人说的话使用一些规则自己构建数据集训练biRNN模型，来预测

确定言论结束方式切换：

        GET /cmd/extractor: 查询当前使用的判断句子结束的模型类型
        GET /cmd/extractor/{type}: 设置判断句子结束的方法，type类型: 
            sif: 句子相似度
            rnn: 是否是人说的话
            mix: 两者综合，默认类型

详见：[project1.md](./project1.md)

## 文本摘要-无监督抽取式
程序入口：auto_summarizer_router.py

解决思路：
1. 为文本每个句子评分，
2. 基于假设文本前20%的内容包含80%信息调整句子评分
3. 根据分数排序，取分值最高的一句最为候选句
4. 应用可配置的规则优化句子内容
5. 指代消解
6. 为了减少文摘句之间的冗余度，需要根据候选句与其他句子的相似度调整剩余句子评分。剩余句子评分-相似度*候选句评分
7. 重复3-6步，直至摘要足够长

句子评分实现了3种方法：
- 经典自动摘要方法

        1.把文章切分成句子
        2.把每个句子转换成向量，并计算两个句子的余弦相似度
        3.利用相似矩阵构建图（graph）
        4.计算图的每一个结点的page rank
       
- 通过词语的text_rank值给句子评分

        1.计算所有词的text_rank值
        2.计算每个句子包含词语的text_rank平均值

- 将文本当作一个长句，计算每个句子与长句的相似度，给句子评分

句子评分及摘要长度参数设置：

        GET /auto_summarizer?rank={rank}&ratio={ratio}&alpha={alpha}
            rank: 评分方法
                sentence_rank：方法一
                text_rank：方法二
                sentence_similarity：方法三
            ratio: 摘要长度与文本长度比例，默认0.2
            alpha: 冗余度系数，减少摘要句子之间的冗余度，(0, 1]，系数越大，冗余度越高，1表示不考虑冗余，默认1

## 聊天机器人
程序入口：chatbot_router.py

解决思路：
1. 使用ball tree查询与输入句子距离最近的10个问题，作为后续句子。句子向量化普林斯顿句子向量论文(https://openreview.net/forum?id=SyK00v5xx)的方法
2. 使用布尔搜索选出10个评分最高的回答，评分方法使用tf-idf
3. 选取回复策略，为了趣味性，回复会在候选句子中随机选择1-3个：

        1. 如果通过聚类找到的句子距离较近（此值可以设置），则直接作为候选句子，然后随机选择1-3个句子返回
        2. 根据聚类和布尔搜索的阈值（这两个值都可以设置）过滤，然后去重合并两个方法的结果，从中随机选择1-3个句子返回
        3. 经过步骤2过滤后，没有候选句子，则：
            - 使用attention-seq2seq生成英文回复，参考(https://github.com/ywk991112/pytorch-chatbot)
            - 模板方法生成回复，模板方法参考狗屁不通文本生成器(https://github.com/menzi11/BullshitGenerator)
        
阈值参数设置：

        GET /chatbot/cluster/nearest/<value> 聚类结果直接返回的阈值设置
        GET /chatbot/cluster/threshold/<value> 聚类阈值设置
        GET /chatbot/search/threshold/<value> 布尔搜索阈值设置

