import jieba
import re
import time
import numpy as np


def cut_sentences(para):
    """
    分句
    :param para:
    :return:
    """
    para = ''.join([p.strip() for p in para.split("\n")])  # 合并换行
    para = re.sub(r'([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub(r'(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号r
    para = re.sub(r'(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub(r'([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return [s for s in para.split("\n") if len(s) > 0]


def cut(string, stop_words=None):
    """
    分词
    :param stop_words:
    :param string:
    :return:
    """
    if not stop_words:
        stop_words = set()

    def token(txt):
        return ''.join(re.findall(r'[\u4e00-\u9fa5]+', txt))

    return [w for w in jieba.lcut(token(string)) if len(w.strip()) > 0 and w not in stop_words]


def cosine_similarity(emb1, emb2):
    """
    计算两个向量余弦相似度
    :param emb1:
    :param emb2:
    :return:
    """
    if type(emb1) == list:
        emb1 = np.array(emb1)
    if type(emb2) == list:
        emb2 = np.array(emb2)
    inn = (emb1 * emb2).sum()
    emb1norm = np.sqrt((emb1 * emb1).sum())
    emb2norm = np.sqrt((emb2 * emb2).sum())
    if emb1norm == 0 or emb2norm == 0:
        return 0
    scores = inn / emb1norm / emb2norm
    return scores


def elapsed(func):
    """ 函数执行时间 """
    def wrapper(*args, **kwargs):
        t = time.time()
        res = func(*args, **kwargs)
        t = time.time() - t
        print('{} elapsed time: {}s'.format(func.__name__, t))
        return res

    return wrapper
