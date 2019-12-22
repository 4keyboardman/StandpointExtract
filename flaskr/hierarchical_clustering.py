import os

import pandas as pd
from sklearn.neighbors.ball_tree import BallTree

from flaskr.utils import *


def question2vec(sif_model, source_dir):
    """ 用sif将所有的问题转换为向量保存 """
    corpus_file = os.path.join(source_dir, 'qa_corpus.csv')
    content = pd.read_csv(corpus_file).dropna()
    questions = content['question'].tolist()

    sen2vec_file = os.path.join(source_dir, 'qa_corpus_vec.txt')
    # 保存问题向量
    with open(sen2vec_file, 'w', encoding='utf-8') as f:
        for i, s in enumerate(questions):
            sen2vec = sif_model.sentence2vec([s])
            f.write(str(i) + '\t' + ','.join([str(e) for e in sen2vec]) + '\n')


def load_qa_corpus_vec(source):
    """ 加载预先处理的问题向量 """
    res = []
    with open(source, 'r', encoding='utf-8') as f:
        for line in f:
            sp = line.split('\t')
            vec = [float(i) for i in sp[1].split(',')]
            res.append(vec)
    return res


class ClusterModel:
    def __init__(self, sen2vec, corpus_path, corpus_vec_path):
        self.sen2vec = sen2vec

        self._corpus = pd.read_csv(corpus_path)
        self._vectors = load_qa_corpus_vec(corpus_vec_path)
        self._indices = []
        X = []
        for i, v in enumerate(self._vectors):
            if any(v):
                self._indices.append(i)
                X.append(v)
        X = np.array(X)
        # 构建balltree
        self.tree = BallTree(X)

    def __call__(self, sentence, k=1):
        """ 找出与给定句子相似的topk个问题 """
        x = self.sen2vec.sentence2vec([sentence]).reshape(1, -1)
        dist, ind = self.tree.query(x, k=k)
        res = []
        indices = [self._indices[i] for i in ind[0]]
        for i, e in enumerate(indices):
            qa = self._corpus.loc[e]
            res.append((qa['question'], qa['answer'], dist[0][i]))
        return res
