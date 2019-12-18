from flask import current_app
import random

from flaskr.utils import *


def handle(message):
    """ 根据输入信息返回回复内容 """
    chatbot = current_app.nlp_model.chatbot
    cluster = chatbot.cluster
    search_engine = chatbot.search_engine
    # 聚类
    cluster_res = cluster(message, 10)
    cluster_res = dist_2_prob(reversed(cluster_res))
    # 搜索
    search_res = search_engine(message, 10)
    search_res = dist_2_prob(reversed(search_res))
    # 综合聚类和搜索结果排序
    reply = score(cluster_res, search_res)
    # 随机取top1-3句
    reply = reply[:random.randint(1, 3)]
    # 过滤得分低的句子
    reply = [i for i in reply if i[1] >= chatbot.threshold]
    # 没有找到句子，使用模板生成文本
    if len(reply) == 0:
        generate_text = chatbot.template_generator(message, 200)
        reply = [(generate_text, 0)]
    return reply


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
    def __init__(self, cluster, search_engine, template_generator, threshold=0.1):
        self.cluster = cluster
        self.search_engine = search_engine
        self.template_generator = template_generator
        self.threshold = threshold  # 得分阈值
