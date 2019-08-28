import os

from flaskr import SIF_embedding
from flaskr import speck_classifier
from flaskr import extractor

from flask import Flask
from gensim.models import Word2Vec


def get_related_words(initial_words, model):
    """
    @initial_words are initial words we already know
    @model is the word2vec model
    """

    class Node:
        """
        搜索相近词树的节点
        """

        def __init__(self, name: str, pre: str, deep: int, weight: float):
            self.name = name  # 节点名称
            self.pre = pre  # 上一个节点
            self.deep = deep  # 搜索深度
            self.weight = weight  # 节点权重

        def __str__(self):
            return str((self.name, self.pre, self.deep, self.weight))

    from collections import defaultdict
    unseen = [Node(w, None, 0, 1) for w in initial_words]
    seen = defaultdict(Node)
    max_size = 500  # could be greater
    while unseen and len(seen) < max_size:
        node = unseen.pop(0)
        if node.name in seen:
            node.weight += seen[node.name].weight
        else:
            new_expanding = [Node(w, node.name, node.deep + 1, s * node.weight)
                             for w, s in model.wv.most_similar(node.name, topn=20) if w != node.name]
            unseen += new_expanding
        seen[node.name] = node
        # optimal: 1. score function could be revised
        # optimal: 2. using dymanic programming to reduce computing time
    return [n.name for n in sorted(seen.values(), key=lambda o: o.weight, reverse=True)[:100]]


def gen_say_words(word2vec_model, path, initial_words):
    say_words = get_related_words(initial_words, word2vec_model)
    with open(path, 'w') as f:
        for w in say_words:
            f.write(w + '\n')


def load_say_words(w2v_model, say_words_path, init_say_words_path):
    def read(path):
        with open(path, encoding="utf-8") as f:
            data = [line.strip() for line in f]
        return data

    if not os.path.isfile(say_words_path):
        gen_say_words(w2v_model, say_words_path, read(init_say_words_path))
    return read(say_words_path)


def load_stop_words(path):
    stop_words = set()
    if not os.path.isfile(path):
        return stop_words
    with open(path, encoding="utf-8") as f:
        for line in f:
            stop_words.add(line.strip())
    return stop_words


def load_sif_model(word2vec_model, stop_words):
    return SIF_embedding.SIFModel(word2vec_model, stop_words)


def load_rnn_model(vocab_path, rnn_model_path):
    vocab = speck_classifier.load_vocabulary(vocab_path)
    return speck_classifier.load_model(rnn_model_path, vocab)


class NLPModel:
    """
    全局模型参数
    """

    def __init__(self, word2vec_model, say_words, stop_words, sif_model, rnn_model):
        self.rnn_model = rnn_model
        self.sif_model = sif_model
        self.stop_words = stop_words
        self.say_words = say_words
        self.word2vec_model = word2vec_model
        self.sif_extractor = extractor.SIFExtractor(sif_model, say_words)
        self.rnn_extractor = extractor.RNNExtractor(rnn_model, say_words)
        # 默认使用rnn
        self.extractor = self.rnn_extractor


def init_model(app: Flask):
    """
    初始化word2vec模型
    """
    app.logger.info("start initialize...")
    instance_path = app.instance_path
    app.logger.info("app instance path: {}".format(instance_path))

    # 加载word2vec
    word2vec_model_path = os.path.join(instance_path, 'word2vec.model')
    app.logger.info("load word2vec model: {}".format(word2vec_model_path))
    word2vec_model = Word2Vec.load(word2vec_model_path)

    # 获取说的相近词
    init_say_words_path = os.path.join(instance_path, 'init_say_words.txt')
    say_words_path = os.path.join(instance_path, 'say_words.txt')
    app.logger.info("get say words: {}".format(say_words_path))
    say_words = load_say_words(word2vec_model, say_words_path, init_say_words_path)

    # 加载停用词
    stop_words_path = os.path.join(instance_path, 'stop_words.txt')
    app.logger.info("load stop words: {}".format(say_words_path))
    stop_words = load_stop_words(stop_words_path)

    # 加载sif模型
    app.logger.info("load sif model: {}".format(say_words_path))
    sif_model = load_sif_model(word2vec_model, stop_words)

    # 加载rnn模型
    vocab_path = os.path.join(instance_path, 'vocabulary.txt')
    rnn_model_path = os.path.join(instance_path, 'rnn_model')
    app.logger.info("load rnn model: {},{}".format(vocab_path, rnn_model_path))
    rnn_model = load_rnn_model(vocab_path, rnn_model_path)

    app.nlp_model = NLPModel(word2vec_model, say_words, stop_words, sif_model, rnn_model)
    app.logger.info("initialize over.")