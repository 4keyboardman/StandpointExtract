from functools import lru_cache

from flaskr.utils import *
from pyhanlp import *
from flaskr.SIF_embedding import SIFModel
from flaskr.speck_classifier import BiRNN


class WordNode:
    """
    构建依存树节点
    """

    def __init__(self, ID, NAME, LEMMA, DEPREL, POSTAG, CPOSTAG):
        self.ID = ID
        self.NAME = NAME
        self.LEMMA = LEMMA
        self.DEPREL = DEPREL
        self.POSTAG = POSTAG
        self.CPOSTAG = CPOSTAG
        self.parent = None
        self.children = {}


def parse_sentence(sentence):
    """
    句子依存分析，构建依存树
    """
    # 依存分析
    parsed_sentence = HanLP.parseDependency(sentence)
    # 构建依存树
    node_dict = {}
    trie = None
    for word in parsed_sentence.iterator():
        head = word.HEAD
        if word.ID in node_dict:
            node = node_dict[word.ID]
        else:
            node = WordNode(word.ID, word.NAME, word.LEMMA, word.DEPREL, word.POSTAG, word.CPOSTAG)
            node_dict[word.ID] = node
        if head.ID in node_dict:
            parent = node_dict[head.ID]
        else:
            parent = WordNode(head.ID, head.NAME, head.LEMMA, head.DEPREL, head.POSTAG, head.CPOSTAG)
            node_dict[head.ID] = parent
        if head.ID == 0:
            trie = node
        node.parent = parent
        parent.children[node.ID] = node
    return parsed_sentence, trie


def search_trie(trie, predicate):
    unseen = [trie]
    while len(unseen) > 0:
        node = unseen.pop(0)
        if predicate(node):
            return node
        unseen += node.children.values()
    return None


def build_sentence(node, sentence=''):
    children = node.children.values()
    if len(children) == 0:
        return sentence + node.LEMMA
    left = [c for c in children if c.ID < node.ID]
    right = [c for c in children if c.ID > node.ID]
    for c in left:
        sentence = build_sentence(c, sentence)
    sentence += node.LEMMA
    for c in right:
        sentence = build_sentence(c, sentence)
    return sentence


def parse_say(node):
    def is_entity(w):
        """判断是否为实体"""
        return w.POSTAG.startswith('n')

    entity = None

    # 查找说话实体
    children = node.children.values()
    for word in children:
        if word.DEPREL == '主谓关系':
            if is_entity(word):
                entity = word.LEMMA
                continue
            else:
                return None, None
        elif word.DEPREL == '状中结构' and not entity:
            # 状中结构查找实体
            entity_node = search_trie(word, is_entity)
            if entity_node:
                entity = entity_node.LEMMA
                continue
        else:
            pass
    # 使用并列的词继续查找
    if not entity and node.DEPREL == '并列关系':
        entity, _ = parse_say(node.parent)
    if not entity:
        return None, None
    # 获取实体说的话
    exclude_relation = {'主谓关系', '状中结构', '间宾关系'}     # 非说话内容关系
    sentence = ''
    speck_words = [c for c in children if c.DEPREL not in exclude_relation]
    for w in speck_words:
        sentence += build_sentence(w)
    return entity, sentence


def search_speck(word_trie, say_words):
    """
    查找说话实体及内容
    :param word_trie:
    :param say_words:
    :return:
    """
    unseen = [word_trie]
    while len(unseen) > 0:
        node = unseen.pop(0)
        children = node.children.values()
        unseen += children
        if node.LEMMA in say_words:
            return parse_say(node)
    return None, None


def search(parsed_sentence, root_id, speaker_id):
    """
    :root_id: id for "说"
    :speaker_id: speaker name word id
    :target_id: target word id, search whether it belong to "说"
    search the entire sentence, all tokens that belong to root and not belong to speaker is the result
    """
    result = ''
    for word in parsed_sentence.iterator():
        if check_word(parsed_sentence, root_id, speaker_id, word):
            result += word.LEMMA
    return result


@lru_cache(maxsize=32)
def check_word(parsed_sentence, root_id, speaker_id, word):
    """
    :root_id: id for "说"
    :speaker_id: id for speaker
    :word: check if word belong to root and not belong to speaker
    """
    # 状中结构：去除修饰说的成分; 主谓关系：去除说的主语
    except_relation = ['状中结构', '主谓关系', '间宾关系']
    # 标点直接返回
    if word.DEPREL == '标点符号':
        return True
    if word.ID in [speaker_id, 0]:
        return False
    if word.HEAD.ID == root_id and word.DEPREL not in except_relation:
        return True  # 找到
    return check_word(parsed_sentence, root_id, speaker_id, word.HEAD)


def post_process_result(text):
    # 去掉开头标点
    text = re.sub(r'^[：|:|"|“|,|，]+', '', text)
    # 去掉结尾标点
    text = re.sub(r'["|”]+$', '', text)
    return text


class Extractor:

    def extract(self, text: str) -> [['entity', 'standpoint']]:
        """
        根据文本提取人物言论
        :param text:
        :return:
        """
        raise NotImplementedError


class SIFExtractor(Extractor):
    """
    基于SIF方法计算句子相似度，来判断句子结束
    """

    def __init__(self, sif_model: SIFModel, say_words):
        self.sif_model = sif_model
        self.say_words = say_words

    def extract(self, text):
        return self._extract(text, self.say_words, self.sif_model)

    @staticmethod
    def _extract(text, say_words, sif_model):
        def flush_cache(r, c):
            if len(r) > 0 and len(c) > 0:
                r[-1][-1] = ''.join(c)
                c.clear()

        sen_list = [s for s in cut_sentences(text) if len(s) > 0]
        result = []
        cache = []
        for s in sen_list:
            sen_type, entity, sentence = SIFExtractor._search_dependency(s, say_words)
            if 'first' == sen_type:
                flush_cache(result, cache)
                result.append([entity, sentence])
                cache.append(sentence)
            elif 'next' == sen_type and len(cache) > 0:
                cache.append(sentence)
            elif 'candidate' == sen_type and len(cache) > 0 and sif_model.is_next(sentence, ''.join(cache)):
                cache.append(sentence)
            else:
                flush_cache(result, cache)
        flush_cache(result, cache)
        return [[i[0], post_process_result(i[1])] for i in result]

    @staticmethod
    def _search_dependency(sentence, related_words):
        _, trie = parse_sentence(sentence)
        # 寻找说语句
        entity, s = search_speck(trie, related_words)
        if entity:
            return 'first', entity, s
        # 没有找到说语句，则分析句子结构
        children = trie.children.values()
        for c in children:
            if c.DEPREL == '主谓关系':
                if c.POSTAG == 'r':
                    return 'next', c.LEMMA, sentence  # 主语是代词，依赖于前面的句子
                else:
                    return 'candidate', c.LEMMA, sentence  # 完全独立的句子，待确定
            else:
                return 'next', None, sentence  # 句子没有主谓关系，依赖于前面的句子
        return None, None, None


class SpeckExtractor(Extractor):
    """
    基于rnn判断一句话能否作为人说的话，来判断句子结束
    """

    def __init__(self, speck_model: BiRNN, say_words):
        self.say_words = say_words
        self.speck_model = speck_model

    def extract(self, text):
        return self._extract(text, self.say_words, self.speck_model)

    @staticmethod
    def _extract(text, say_words, speck_model):
        def flush_cache(r, c):
            if len(r) > 0 and len(c) > 0:
                r[-1][-1] = ''.join(c)
                c.clear()

        sen_list = [s for s in cut_sentences(text) if len(s) > 0]
        result = []
        cache = []
        for s in sen_list:
            entity, sentence = SpeckExtractor._search_dependency(s, say_words)
            if sentence and speck_model.predict(sentence):
                flush_cache(result, cache)
                result.append([entity, sentence])
                cache.append(sentence)
            elif len(cache) > 0 and speck_model.predict(s):
                cache.append(s)
            else:
                flush_cache(result, cache)
        flush_cache(result, cache)
        return [[i[0], post_process_result(i[1])] for i in result]

    @staticmethod
    def _search_dependency(sentence, related_words):
        """
        input: Chinese text parsed by parse_sentence
        return: (speaker, point)
        """
        _, trie = parse_sentence(sentence)
        return search_speck(trie, related_words)
