from flaskr.utils import *
from flaskr.extractor import parse_sentence
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
    vacab = list(textrank(''.join(sentences), topK=None, withWeight=True,
                          allowPOS=('nr', 'ns', 'nt', 'nw', 'nz', 'n', 'vn', 'vd', 'v', 'eng')))
    index_end = int(len(vacab) * 0.2)
    vacab = {i[0]: i[1] for i in vacab[:index_end]}
    sen_score = {}
    for i, s in enumerate(sentences):
        arr = [vacab[word] for word in jieba.cut(s) if word in vacab]
        score = np.sum(arr) if len(arr) > 0 else 0
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


def apply_reference_resolution(sentence, above_sentence):
    """
    简单基于规则的指代消解
    他，她，它，省略主语
    :param sentence: 待分析句子
    :param above_sentence: 上文
    :return:
    """
    res = []
    subject = ''  # 主语
    parsed_sentence, _ = parse_sentence(sentence)
    # 扫描当前句子
    index = 0
    nh_entity = None  # 人
    n_entity = None  # 其他名词
    nh_pronoun = []  # 他她代词索引
    n_pronoun = []  # 它代词索引
    for word in parsed_sentence.iterator():
        w = word.LEMMA
        res.append(w)
        # 检查主语
        if word.DEPREL == '主谓关系':
            subject = w
        # 检查实体
        if word.POSTAG.startswith('n'):
            if word.CPOSTAG == 'nh':
                nh_entity = w
            else:
                n_entity = w
        # 检查代词
        if word.POSTAG == 'r':
            if w == '他' or w == '她':
                if not nh_entity:
                    nh_pronoun.append(index)
            elif w == '它':
                if not n_entity:
                    n_pronoun.append(index)
        index += 1
    # 没有主语则取上文最近句子的主语
    if len(subject) == 0:
        for i in reversed(above_sentence):
            subject = parse_subject(i)
            if len(subject) > 0:
                res.insert(0, subject)
                break
    # 他她它
    if len(nh_pronoun) > 0 or len(n_pronoun) > 0:
        for i in reversed(above_sentence):
            nh_entity, n_entity = parse_entity(i)
            if len(nh_pronoun) > 0 and len(nh_entity):
                for j in nh_pronoun:
                    res[j] = nh_entity[-1]
                nh_pronoun.clear()
            if len(n_pronoun) > 0 and len(n_entity):
                for j in n_pronoun:
                    res[j] = n_entity[-1]
                n_pronoun.clear()
            if len(nh_pronoun) == 0 and len(n_pronoun) == 0:
                break
    return ''.join(res)


def parse_subject(sentence):
    parsed_sentence, _ = parse_sentence(sentence)
    for word in parsed_sentence.iterator():
        if word.DEPREL == '主谓关系':
            return word.LEMMA
    return ''


def parse_entity(sentence):
    nh_entity = []
    n_entity = []
    parsed_sentence, _ = parse_sentence(sentence)
    for word in parsed_sentence.iterator():
        if word.POSTAG.startswith('n'):
            if word.CPOSTAG == 'nh':
                nh_entity.append(word.LEMMA)
            else:
                n_entity.append(word.LEMMA)
    return nh_entity, n_entity


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
        selected_sentence = apply_reference_resolution(selected_sentence, sentences[:selected[0]])
        sentences[selected[0]] = selected_sentence
        m += len(sentences[selected[0]])
        # 考虑冗余度，实际结果后面的句子有点偏题
        # 根据句子相似度更新句子分数，减少选取句子之间的冗余度
        # for i, v in enumerate(score):
        #     sim = sif_model.sentence_similarity(sentences[selected[0]], sentences[v[0]])
        #     s = v[1] - selected[1] * sim
        #     score[i] = (v[0], s)
        # apply_softmax(score)
    return idx


def summarize(text, n=None, ratio=0.2, rank='sentence_rank'):
    sentences = cut_sentences(text)
    score = eval(rank)(sentences)
    if not n:
        n = int(len(text) * ratio)
    idx = cand_idx(sentences, score, n)
    return ''.join([sentences[i] for i in sorted(idx)])
