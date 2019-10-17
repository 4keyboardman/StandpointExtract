from flaskr.utils import *
from jieba.analyse import textrank
import jieba
import numpy as np
import networkx as nx
from flask import current_app


def text_rank(sentences):
    """
    通过词语的text_rank值给句子评分
    1.计算所有词的text_rank值
    2.计算每个句子包含词语的text_rank平均值
    """
    vacab = dict(textrank(''.join(sentences), topK=None, withWeight=True))
    sen_score = {}
    for i, s in enumerate(sentences):
        arr = [vacab[word] for word in jieba.cut(s) if word in vacab]
        score = np.mean(arr) if len(arr) > 0 else 0
        sen_score[i] = score
    return sen_score


def sentence_rank(sentences):
    """
    经典extractive自动摘要方法
    1.把文章切分成句子
    2.把每个句子转换成向量，并通过consine_similarity计算两个句子之间的相似度
    3.利用相似矩阵构建图（graph）
    4.计算图的每一个结点的page rank
    """
    similarity = current_app.nlp_model.sif_model.sentence_similarity
    # 构建相似度矩阵
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                similarity_matrix[i][j] = similarity(sentences[i], sentences[j])
    # 利用相似矩阵构建图（graph）
    sentence_similarity_graph = nx.from_numpy_array(similarity_matrix)
    # 计算图的每一个结点的page rank
    return nx.pagerank(sentence_similarity_graph)


def sentence_similarity(sentences):
    """
    将文本当作一个长句，计算每个句子与长句的相似度，给句子评分
    """
    sif_model = current_app.nlp_model.sif_model
    doc2vec = sif_model.sentence2vec([''.join(sentences)])
    sen_score = {}
    for i, s in enumerate(sentences):
        sen2vec = sif_model.sentence2vec([s])
        sen_score[i] = sif_model.similarity(doc2vec, sen2vec)
    return sen_score


def softmax(x):
    _x = x - np.max(x)
    ep = np.exp(_x)
    return ep / np.sum(ep)


def simple_cand_idx(sentences, score, n):
    """ 根据评分简单选取句子 """
    m = 0
    idx = []
    score = sorted(score, key=lambda i: i[1], reverse=True)
    for item in score:
        idx.append(item[0])
        m += len(sentences[item[0]])
        if m >= n:
            break
    return idx


def position_prob(length):
    """ 假设前20%文本包含80%内容 """
    a = np.zeros(length)
    n = max(1, int(length * 0.2))
    a[:n] = 1
    return softmax(a)


def apply_postion_prob(score, prob):
    """ 应用句子位置因素 """
    for i, v in enumerate(score):
        score[i] = (v[0], prob[v[0]] + v[1])


def apply_softmax(score):
    prob = softmax([i[1] for i in score])
    for i, v in enumerate(score):
        score[i] = (v[0], prob[i])


def apply_rules(sentence):
    rules = current_app.nlp_model.text_summarization_rules
    for rule in rules:
        condition = rule[0]
        replacements = rule[1]
        if re.search(condition, sentence):
            for r in replacements:
                if len(r) == 0:
                    r = r'.*'
                sentence = re.sub(r, '', sentence)
            return sentence
    return sentence


def cand_idx(sentences, score, n):
    """ 选取候选句子索引 """
    m = 0
    idx = []
    sif_model = current_app.nlp_model.sif_model
    score = list(score.items())
    prob = position_prob(len(score))
    apply_softmax(score)
    apply_postion_prob(score, prob)
    while m <= n and len(score) > 0:
        score = sorted(score, key=lambda i: i[1], reverse=True)
        # 选取分值最高的句子
        selected = score.pop(0)
        idx.append(selected[0])
        selected_sentence = sentences[selected[0]]
        selected_sentence = apply_rules(selected_sentence)
        if len(selected_sentence) == 0:
            continue
        sentences[selected[0]] = selected_sentence
        m += len(sentences[selected[0]])
        # 根据句子相似度更新句子分数，减少选取句子之间的冗余度
        for i, v in enumerate(score):
            sim = sif_model.sentence_similarity(sentences[selected[0]], sentences[v[0]])
            s = v[1] - selected[1] * sim
            score[i] = (v[0], s)
        apply_softmax(score)
    return idx


def summarize(text, n=None, ratio=0.2, rank='sentence_rank'):
    sentences = cut_sentences(text)
    score = eval(rank)(sentences)
    if not n:
        n = int(len(text) * ratio)
    idx = cand_idx(sentences, score, n)
    return ''.join([sentences[i] for i in sorted(idx)])
