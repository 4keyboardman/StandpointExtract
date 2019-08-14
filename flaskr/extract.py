
import os
from get_related_word import load_said
from urils import deal

# 中文分句
def split_sentences(string):
    from pyltp import SentenceSplitter
    sents = SentenceSplitter.split(string) # 分句
    sentences = [s for s in sents if len(s) != 0]
    print(sentences)
    return sentences

# Jieba 分词
def split_words(sentences):
    sents = [deal(s) for s in sentences]
    return sents

# LTP 分词
def splitwords(ltp_model_path,sentences):
    model_path = ltp_model_path  # ltp模型目录的路径
    cws_model_path = os.path.join(model_path, 'cws.model')  # 分词模型路径，模型名称为`cws.model`

    from pyltp import Segmentor
    segmentor = Segmentor()  # 初始化实例
    segmentor.load(cws_model_path)  # 加载模型
    words = [segmentor.segment(s) for s in sentences ] # 分词
    words_list = list(words)

    segmentor.release()  # 释放模型
    return words_list


# 词性标注
def get_word_pos(ltp_model_path, sents):
    model_path = ltp_model_path
    pos_model_path = os.path.join(model_path, 'pos.model')
    from pyltp import Postagger
    postagger = Postagger() # 初始化实例
    postagger.load(pos_model_path) # 加载模型
    postags = [postagger.postag(words.split()) for words in sents]# 词性标注
    postags = [list(w) for w in postags] # 使用list转换成python列表

    postagger.release() # 释放模型
    return postags

# 依存句法分析
def dependency_parsing(ltp_model_path, sents, postags, said):

    LTP_DATA_DIR = ltp_model_path # ltp模型目录的路径
    par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
    ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')     # 命名实体识别模型路径，模型名称为`ner.model`

    from pyltp import Parser, NamedEntityRecognizer
    recognizer = NamedEntityRecognizer() # 初始化实例
    recognizer.load(ner_model_path)  # 加载模型

    parser = Parser()  # 初始化实例
    parser.load(par_model_path)  # 加载模型

    contents = []
    for index in range(len(sents)):
        words = sents[index].split()

        pos = postags[index]

        netags = recognizer.recognize(words, pos)  # 命名实体识别
        # print("netags", list(netags))
        netags = list(netags) # 使用list转换成python列表
        # LTP 提供的命名实体类型为：人名(Nh)、地名(Ns)、机构名(Ni)
        if ('S-Ns' not in netags) and ('S-Ni' not in netags) and ('S-Nh' not in netags):
            continue

        arcs = parser.parse(words, pos)  # 依存句法分析

        arcs = [(arc.head, arc.relation) for arc in arcs]
        # arc.head 表示依存弧的父节点词的索引。ROOT节点的索引是0，第一个词开始的索引依次为1、2、3…
        # arc.relation 表示依存弧的关系。

        # SBV：主谓关系，subject-verb,我送她一束花(我<-送)
        arcs = [(i, arc) for i, arc in enumerate(arcs) if arc[1] == 'SBV']
        for arc in arcs:
            verb = arc[1][0]
            subject = arc[0]
            if words[verb - 1] not in said:
                continue

            contents.append((words[subject], words[verb - 1], ''.join(words[verb:])))
    # parser.release()  # 释放模型
    # recognizer.release()  # 释放模型
    return contents


def extract(text):
    """
    新闻人物言论提取
    :param text:
    :return:
    """
    # 加载“说”的近义词
    path = "./"
    said = load_said(path + "similar_said.txt")

    ltp_model_path = './model/ltp_data/'
    # 中文分句：对输入的文本进行分句
    sentences = split_sentences(string)
    # 中文分词(jieba)
    sents = split_words(sentences)
    # sents = splitwords(ltp_model_path,sentences)
    # 词性标注
    postags = get_word_pos(ltp_model_path, sents)
    # 依存句法分析
    contents = dependency_parsing(ltp_model_path, sents, postags, said)
    contents_dict = {}
    for indx, ones in enumerate(contents):
        contents_dict[str(indx)] = [ones[0], ones[1], ones[2]]

    return contents_dict



if __name__ == '__main__':
    string = """
    13日上午，在以视频会议形式召开的省委理论学习中心组第三十七次集体(扩大)学习暨“龙江发展讲坛”专题报告会上，省委书记、省人大常委会主任张庆伟就防范应对台风暴雨天气和防汛工作进行安排部署。
    他指出，当前全省正处于主汛期，受台风外围云系影响，暴雨天气增多，防汛形势十分严峻，必须克服麻痹思想和侥幸心理，把各项防汛抗灾措施落实到位，确保人民群众生命财产安全。

　　张庆伟强调，要时刻保持高度警惕，及时关注雨情信息，掌握汛情走势，做好险情研判，加强防洪安全隐患排查，及时发布安全预警信息。
   要强化应急处置，提前做好防范工作，完善工作预案，聚焦重点区域严防严守，做好电力、交通、通信、医疗等方面应急抢险准备，确保出现灾情及时有效处置。
   要搞好抢险救灾，及时组织抢险救援，提前做好人员转移避险，最大程度减少灾害损失，确保不发生人员伤亡。
   要压实落靠责任，各地要迅速行动、精心组织，各级领导要分兵把口、靠前指挥，相关部门要密切联系、加强协作，形成防汛工作合力，确保安全度汛。
    """
    print( extract(string) )
