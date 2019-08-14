import re
from functools import lru_cache
from pyhanlp import *
import jieba.posseg as psg
from flaskr.nlp_model import WordModel


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


def search_dependency(parsed_sentence, related_words):
    """
    input: Chinese text parsed by parse_sentence
    return: {speaker: point}
    """
    result = []
    for word in parsed_sentence.iterator():
        if (word.POSTAG.startswith('n') or word.POSTAG == 'r') \
                and word.DEPREL == '主谓关系' and word.HEAD.LEMMA in related_words:
            # TODO: if word.LEMMA is 代词， 指代消解
            speaker_id = word.ID
            root_id = word.HEAD.ID
            content = search(parsed_sentence, root_id, speaker_id)
            if len(content) > 0:
                content = post_process_result(content)
                result = [word.LEMMA, content]  # word.LEMMA为发表观点的人
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


def cut_sentences(para):
    """
    分句
    :param para:
    :return:
    """
    para = re.sub(r'([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub(r'(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号r
    para = re.sub(r'(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub(r'([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return para.split("\n")


def process_sentence(sentence):
    """
    句子分词
    :param sentence:
    :return:
    """
    exclude_flags = {'eng', 'x'}
    return [p.word for p in psg.lcut(sentence) if not any([p.flag.startswith(flag) for flag in exclude_flags])]


def extract(text, word_model: WordModel):
    res = [search_dependency(parse_sentence(s), word_model.say_words) for s in cut_sentences(text) if len(s) > 0]
    return [i for i in res if len(i) > 0]
