from flaskr.utils import *

import numpy as np
from sklearn.decomposition import TruncatedSVD


def get_weighted_average(We, x, w):
    """
    Compute the weighted average vectors
    :param We: We[i,:] is the vector for word i
    :param x: x[i, :] are the indices of the words in sentence i
    :param w: w[i, :] are the weights for the words in sentence i
    :return: emb[i, :] are the weighted average vector for sentence i
    """
    n_samples = x.shape[0]
    emb = np.zeros((n_samples, We.shape[1]))
    for i in range(n_samples):
        emb[i, :] = w[i, :].dot(We[x[i, :], :]) / np.count_nonzero(w[i, :])
    return emb


def compute_pc(X, npc=1):
    """
    Compute the principal components. DO NOT MAKE THE DATA ZERO MEAN!
    :param X: X[i,:] is a data point
    :param npc: number of principal components to remove
    :return: component_[i,:] is the i-th pc
    """
    svd = TruncatedSVD(n_components=npc, n_iter=7, random_state=0)
    svd.fit(X)
    return svd.components_


def remove_pc(X, npc=1):
    """
    Remove the projection on the principal components
    :param X: X[i,:] is a data point
    :param npc: number of principal components to remove
    :return: XX[i, :] is the data point after removing its projection
    """
    pc = compute_pc(X, npc)
    if npc == 1:
        XX = X - X.dot(pc.transpose()) * pc
    else:
        XX = X - X.dot(pc.transpose()).dot(pc)
    return XX


def SIF_embedding(We, x, w, params):
    """
    Compute the scores between pairs of sentences using weighted average + removing the projection on the first principal component
    :param We: We[i,:] is the vector for word i
    :param x: x[i, :] are the indices of the words in the i-th sentence
    :param w: w[i, :] are the weights for the words in the i-th sentence
    :param params.rmpc: if >0, remove the projections of the sentence embeddings to their first principal component
    :return: emb, emb[i, :] is the embedding for sentence i
    """
    emb = get_weighted_average(We, x, w)
    if params.rmpc > 0:
        emb = remove_pc(emb, params.rmpc)
    return emb


def getWordWeight(word_frequency, a=1e-3):
    if a <= 0:  # when the parameter makes no sense, use unweighted
        a = 1.0
    word2weight = {}
    N = 0
    for w, f in word_frequency.items():
        word2weight[w] = f
        N += f
    for key, value in word2weight.items():
        word2weight[key] = a / (a + value / N)
    return word2weight


def sentences2idx(sentences, words):
    """
    Given a list of sentences, output array of word indices that can be fed into the algorithms.
    :param sentences: a list of sentences
    :param words: a dictionary, words['str'] is the indices of the word 'str'
    :return: x1, m1. x1[i, :] is the word indices in sentence i, m1[i,:] is the mask for sentence i (0 means no word at the location)
    """
    seq1 = []
    for s in sentences:
        seq1.append(getSeq(s, words))
    x1, m1 = prepare_data(seq1)
    return x1, m1


def prepare_data(list_of_seqs):
    lengths = [len(s) for s in list_of_seqs]
    n_samples = len(list_of_seqs)
    maxlen = np.max(lengths)
    x = np.zeros((n_samples, maxlen)).astype('int32')
    x_mask = np.zeros((n_samples, maxlen)).astype('float32')
    for idx, s in enumerate(list_of_seqs):
        x[idx, :lengths[idx]] = s
        x_mask[idx, :lengths[idx]] = 1.
    x_mask = np.asarray(x_mask, dtype='float32')
    return x, x_mask


def getSeq(s, words_map):
    idx = []
    for w in s:
        if w in words_map:
            idx.append(words_map[w])
        else:
            idx.append(len(words_map) - 1)
    return idx


def getWeight(words, word2weight):
    weight4ind = {}
    for word, ind in words.items():
        if word in word2weight:
            weight4ind[ind] = word2weight[word]
        else:
            weight4ind[ind] = 1.0
    return weight4ind


def seq2weight(seq, mask, weight4ind):
    weight = np.zeros(seq.shape).astype('float32')
    for i in range(seq.shape[0]):
        for j in range(seq.shape[1]):
            if mask[i, j] > 0 and seq[i, j] >= 0:
                weight[i, j] = weight4ind[seq[i, j]]
    weight = np.asarray(weight, dtype='float32')
    return weight


class params(object):

    def __init__(self):
        self.LW = 1e-5
        self.LC = 1e-5
        self.eta = 0.05

    def __str__(self):
        t = "LW", self.LW, ", LC", self.LC, ", eta", self.eta
        t = map(str, t)
        return ' '.join(t)


class SIFModel:
    def __init__(self, word2vec_model, stop_words, weightpara=1e-3):
        """
        :param word2vec_model: word2vec模型
        :param stop_words: 停用词
        :param weightpara:
        """
        self.stop_words = stop_words
        self.word2vec_model = word2vec_model
        words = word2vec_model.wv.index2word
        self.word_vectors = word2vec_model.wv.vectors
        word_frequency = {w: v.count for w, v in word2vec_model.wv.vocab.items()}
        self.word_index_map = {w: n for n, w in enumerate(words)}
        word2weight = getWordWeight(word_frequency, weightpara)
        self.weight4ind = getWeight(self.word_index_map, word2weight)

    def sentence_similarity(self, s1, s2):
        if type(s1) == list:
            s1_embdding = self.sentence2vec(s1)
        else:
            s1_embdding = self.sentence2vec([s1])
        if type(s2) == list:
            s2_embdding = self.sentence2vec(s2)
        else:
            s2_embdding = self.sentence2vec([s2])
        return cosine_similarity(s1_embdding, s2_embdding)

    def sentence2vec(self, sentences):
        """
        计算句子向量
        :param sentences:
        :return:
        """
        sens = [cut(s, self.stop_words) for s in sentences]
        sens = [i for i in sens if len(i) > 0]
        if len(sens) == 0:
            return np.zeros(self.word_vectors.shape[1])
        x, m = sentences2idx(sens, self.word_index_map)
        w = seq2weight(x, m, self.weight4ind)
        p = params()
        p.rmpc = 0 if len(sentences) <= 1 else 1
        return SIF_embedding(self.word_vectors, x, w, p)[0]

    def is_next(self, s1, s2, threshold=0.5):
        return self.sentence_similarity(s1, s2) >= threshold
