from functools import lru_cache

from flaskr.utils import *
from pyhanlp import *


def parse_sentence(sentence):
    """
    句子依存分析
    """
    return HanLP.parseDependency(sentence)


def post_process_result(text):
    # 去掉开头标点
    text = re.sub(r'^[：|:|"|“|,|，]+', '', text)
    # 去掉结尾标点
    text = re.sub(r'["|”]+$', '', text)
    return text


def search_dependency(sentence, related_words):
    """
    input: Chinese text parsed by parse_sentence
    return: {speaker: point}
    """
    parsed_sentence = parse_sentence(sentence)
    result = tuple()
    for word in parsed_sentence.iterator():
        root = word.HEAD
        if word.DEPREL == '主谓关系' and root.DEPREL == '核心关系':
            # TODO: if word.LEMMA is 代词， 指代消解
            speaker_id = word.ID
            if word.POSTAG.startswith('n') and word.HEAD.LEMMA in related_words:
                content = search(parsed_sentence, root.ID, speaker_id)
                result = ['first', word.LEMMA, content]  # word.LEMMA为发表观点的人
            elif word.POSTAG == 'r':
                result = ('next', word.LEMMA, sentence)  # 主语是代词的候选句子
            else:
                result = ('candidate', word.LEMMA, sentence)
    if len(result) == 0:
        result = ('next', None, sentence)  # 没有主语的候选句子
    return result


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
    except_relation = ['状中结构', '主谓关系']
    if word.ID in [speaker_id, 0]:
        return False
    if word.HEAD.ID == root_id and word.DEPREL not in except_relation:
        return True  # 找到
    return check_word(parsed_sentence, root_id, speaker_id, word.HEAD)


def extract(text, say_words, sif_model):
    def flush_cache(r, c):
        if len(r) > 0 and len(c) > 0:
            r[-1][-1] = ''.join(c)
            c.clear()
    sen_list = [s for s in cut_sentences(text) if len(s) > 0]
    result = []
    cache = []
    for s in sen_list:
        sen_type, entity, sentence = search_dependency(s, say_words)
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
