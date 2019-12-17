import os
import pickle
from functools import reduce
from operator import and_

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.neighbors import DistanceMetric

from flaskr.utils import *


def dump_tfidf_model(answers, target):
    cut_answers = [' '.join(cut(n)) for n in answers]
    vectorized = TfidfVectorizer(max_features=10000)
    X = vectorized.fit_transform(cut_answers)
    with open(target, 'wb') as f:
        pickle.dump((vectorized, X), f)


def load_tfidf_model(source):
    with open(source, 'rb') as f:
        return pickle.load(f)


def distance(v1, v2):
    return euclidean_distances(v1, v2)


class SearchEngine:
    def __init__(self, corpus_path):
        base_dir = os.path.dirname(corpus_path)
        # TfidfVectorizer序列化文件
        tfidf_file = os.path.join(base_dir, 'qa_tfidf_model.pkl')
        content = pd.read_csv(corpus_path).dropna()
        self.questions = content['question'].tolist()
        self.answers = content['answer'].tolist()
        # 加载TfidfVectorizer
        if not os.path.isfile(tfidf_file):
            dump_tfidf_model(self.answers, tfidf_file)
        self.vectorized, self.X = load_tfidf_model(tfidf_file)
        self.transposed_x = self.X.transpose().toarray()
        self.word_2_id = self.vectorized.vocabulary_

    def __call__(self, query, k=None):
        """
        布尔搜索
        """
        words = cut(query)
        candidates_ids = [self.word_2_id[w] for w in words]
        documents_ids = [set(np.where(self.transposed_x[_id])[0]) for _id in candidates_ids]
        merged_documents = reduce(and_, documents_ids)
        query_vec = self.vectorized.transform([' '.join(words)]).toarray()[0]
        # 按距离排序
        doc_dist = [(self.questions[i], self.answers[i], distance([query_vec], self.X[i].toarray())[0, 0]) for i in merged_documents]
        sorted_doc = sorted(doc_dist, key=lambda i: i[2])
        return sorted_doc[:k]
