from flask import current_app
import random

from flaskr.utils import *


def handle(message):
    """ 根据输入信息返回回复内容 """
    chatbot = current_app.nlp_model.chatbot
    cluster = chatbot.cluster
    search_engine = chatbot.search_engine
    cluster_threshold = chatbot.cluster_threshold
    cluster_nearest = chatbot.cluster_nearest
    search_threshold = chatbot.search_threshold
    # 聚类
    cluster_res = cluster(message, 10)
    # 如果有非常接近的问题，则优先取些句子
    nearest = set([i[1] for i in cluster_res if i[2] < cluster_nearest])
    if len(nearest) > 0:
        return random_choose(nearest)
    # 搜索
    search_res = search_engine(message, 10)
    # 过滤
    cluster_res = [i[1] for i in cluster_res if i[2] < cluster_threshold]
    search_res = [i[1] for i in search_res if i[2] < search_threshold]
    # 去重
    cands = set(cluster_res + search_res)
    # 没有找到句子，使用模板生成文本
    if len(cands) == 0:
        reply = chatbot.template_generator(message, random.randint(10, 600))
    else:
        # 随机取聚类和搜索top1-3句
        reply = random_choose(cands)
    return reply


def random_choose(s, n=3):
    res = list(s)
    random.shuffle(res)
    if len(res) >= n:
        res = res[:random.randint(1, n)]
    return res


def dist_2_prob(qa_dists):
    """ 将距离转换为概率 """
    # 按回答去重
    d = {i[1]: -i[2] for i in qa_dists}
    replys = d.keys()
    values = list(d.values())
    if len(values) == 0:
        return dict()
    dists = softmax(values)
    return {reply: prob for reply, prob in zip(replys, dists)}


def score(cluster_res, search_res):
    """ 综合聚类和搜索结果排序, 权重各占0.5 """
    # 聚类所占比重
    r = 0.5
    for k, v in search_res.items():
        if k in cluster_res:
            cluster_res[k] = cluster_res[k] * r + (1 - r) * v
        else:
            cluster_res[k] = v
    return sorted(cluster_res.items(), key=lambda i: i[1], reverse=True)


class Chatbot:
    def __init__(self, cluster, search_engine, template_generator, cluster_threshold=10, cluster_nearest=3,
                 search_threshold=0.5):
        self.cluster = cluster
        self.search_engine = search_engine
        self.template_generator = template_generator
        self.cluster_threshold = cluster_threshold
        self.cluster_nearest = cluster_nearest
        self.search_threshold = search_threshold
