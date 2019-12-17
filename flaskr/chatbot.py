from flask import current_app
import random

from flaskr.utils import *


def handle(message):
    cluster = current_app.nlp_model.cluster
    search_engine = current_app.nlp_model.search_engine
    # 聚类
    cluster_res = cluster(message, 10)
    cluster_res = dist_2_prob(reversed(cluster_res))
    # 搜索
    search_res = search_engine(message, 10)
    search_res = dist_2_prob(reversed(search_res))
    # 聚类所占比重
    r = 0.5
    for k, v in search_res.items():
        if k in cluster_res:
            cluster_res[k] = cluster_res[k] * r + (1 - r) * v
        else:
            cluster_res[k] = v
    reply = sorted(cluster_res.items(), key=lambda i: i[1], reverse=True)
    return reply[:random.randint(1, 3)]


def dist_2_prob(qa_dists):
    # 按回答去重
    d = {i[1]: -i[2] for i in qa_dists}
    replys = d.keys()
    dists = softmax(list(d.values()))
    return {reply: prob for reply, prob in zip(replys, dists)}
