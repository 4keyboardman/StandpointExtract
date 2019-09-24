from flaskr.utils import *
from jieba.analyse import textrank
import jieba
import numpy as np
from flask import current_app


def text_rank(sentences, **kwargs):
    vacab = dict(textrank(''.join(sentences), topK=None, withWeight=True, **kwargs))
    sen_score = {}
    for i, s in enumerate(sentences):
        score = np.mean([vacab[word] for word in jieba.cut(s) if word in vacab])
        sen_score[i] = score
    return sen_score


def sentence_similarity(sentences, **kwargs):
    sif_model = current_app.nlp_model.sif_model
    doc2vec = sif_model.sentence2vec([''.join(sentences)])
    sen_score = {}
    for i, s in enumerate(sentences):
        sen2vec = sif_model.sentence2vec([s])
        sen_score[i] = sif_model.similarity(doc2vec, sen2vec)
    return sen_score


def summarize(text, n=None, ratio=0.2, rank='text_rank', **kwargs):
    sentences = cut_sentences(text)
    score = eval(rank)(sentences, **kwargs)
    sorted_score = sorted(score.items(), key=lambda i: i[1], reverse=True)
    if not n:
        n = int(len(text) * ratio)
    m = 0
    cand_idx = []
    for item in sorted_score:
        cand_idx.append(item[0])
        m += len(sentences[item[0]])
        if m >= n:
            break
    return ''.join([sentences[i] for i in sorted(cand_idx)])
