import pytest

from flaskr.auto_summarizer import *


@pytest.mark.parametrize("text", ["""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。"""
                                  ])
def test_text_rank(text):
    sentences = cut_sentences(text)
    res = text_rank(sentences)
    res = sorted(res.items(), key=lambda i: i[1], reverse=True)
    print([(sentences[i[0]].strip(), i[1]) for i in res])


@pytest.mark.parametrize("text", ["""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。"""
                                  ])
def test_sentence_similarity(app, text):
    with app.app_context():
        sentences = cut_sentences(text)
        res = sentence_similarity(sentences)
        res = sorted(res.items(), key=lambda i: i[1], reverse=True)
        print([(sentences[i[0]].strip(), i[1]) for i in res])


@pytest.mark.parametrize("text", ["""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。"""
                                  ])
def test_sentence_rank(app, text):
    with app.app_context():
        sentences = cut_sentences(text)
        res = sentence_rank(sentences)
        print(res)


txt = """网易娱乐7月21日报道  林肯公园主唱查斯特·贝宁顿Chester Bennington于今天早上，在洛杉矶 帕洛斯弗迪斯的一个私人庄园自缢身亡，年仅41岁。此消息已得到洛杉矶警方证实。
洛杉矶警方透露，Chester的家人正在外地度假，Chester独自在家，上吊地点是家里的二楼。一说是一名音乐公司工作人员来家里找他时发现了尸体，也有人称是佣人最早发现其死亡。
林肯公园另一位主唱麦克·信田确认了Chester Bennington自杀属实，并对此感到震惊和心痛，称稍后官方会发布声明。Chester昨天还在推特上转发了一条关于曼哈顿垃圾山的新闻。粉丝们纷纷在该推文下留言，不相信Chester已经走了。
外媒猜测，Chester选择在7月20日自杀的原因跟他极其要好的朋友、Soundgarden（声音花园）乐队以及Audioslave乐队主唱Chris Cornell有关，因为7月20日是Chris Cornell的诞辰。而Chris Cornell 于今年5月17日上吊自杀，享年52岁。Chris去世后，Chester还为他写下悼文。
对于Chester的自杀，亲友表示震惊但不意外，因为Chester曾经透露过想自杀的念头，他曾表示自己童年时被虐待，导致他医生无法走出阴影，也导致他长期酗酒和嗑药来疗伤。目前，洛杉矶警方仍在调查Chester的死因。
据悉，Chester与毒品和酒精斗争多年，年幼时期曾被成年男子性侵，导致常有轻生念头。Chester生前有过2段婚姻，育有6个孩子。
林肯公园在今年五月发行了新专辑《多一丝曙光One More Light》，成为他们第五张登顶Billboard排行榜的专辑。而昨晚刚刚发布新单《Talking To Myself》MV。"""


@pytest.mark.parametrize(("text", "rank"), [(txt, "sentence_rank"),
                                            (txt, "text_rank"),
                                            (txt, "sentence_similarity")])
def test_summarize(app, text, rank):
    with app.app_context():
        print(summarize(text, rank=rank))
