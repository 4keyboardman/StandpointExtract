import os

from flask import Flask
from gensim.models import Word2Vec
from flaskr import SIF_embedding


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


class WordModel:
    """
    词向量模型数据，放到应用上下文中作为全局变量
    """

    def __init__(self, word2vec_model, say_words, stop_words):
        self.say_words = say_words
        self.stop_words = stop_words
        self.word2vec_model = word2vec_model
        self.sif_model = SIF_embedding.SIFModel(word2vec_model, stop_words)


def gen_say_words(word2vec_model, path, initial_words):
    say_words = get_related_words(initial_words, word2vec_model)
    with open(path, 'w') as f:
        for w in say_words:
            f.write(w + '\n')


def load_say_words(path):
    say_words = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            say_words.append(line.strip())
    return say_words


def load_stop_words(path):
    stop_words = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            stop_words.add(line.strip())
    return stop_words


def load_model(model_path):
    """
    加载word2vec模型，并获取计算SIF_embdding所需的权重
    :param model_path:  模型文件路径
    :return:
    """
    # 加载word2vec模型
    w2v_model = Word2Vec.load(model_path)
    # 获取说相近的词
    say_words_path = r'resource/say_words'
    if not os.path.isfile(say_words_path):
        gen_say_words(w2v_model, say_words_path, ['说', '透露', '表示', '强调', '宣称', '提出', '指出'])
    say_words = load_say_words(say_words_path)
    stop_words = load_stop_words(r"resource/stop_words")
    return WordModel(w2v_model, say_words, stop_words)


def init_model(app: Flask):
    """
    初始化word2vec模型
    """
    app.logger.info("load model...")
    app.config['word2vec_model_path'] = os.getenv('WORD2VEC_MODEL_PATH',
                                                  os.path.join(app.instance_path, 'model', 'word2vec.model'))
    app.word_model = load_model(app.config['word2vec_model_path'])
    app.logger.info("load model success")
