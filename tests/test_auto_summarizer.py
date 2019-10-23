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


txt = """网易娱乐7月21日报道  林肯公园主唱查斯特·贝宁顿Chester Bennington于今天早上，在洛杉矶帕洛斯弗迪斯的一个私人庄园自缢身亡，年仅41岁。此消息已得到洛杉矶警方证实。
洛杉矶警方透露，Chester的家人正在外地度假，Chester独自在家，上吊地点是家里的二楼。一说是一名音乐公司工作人员来家里找他时发现了尸体，也有人称是佣人最早发现其死亡。
林肯公园另一位主唱麦克·信田确认了Chester Bennington自杀属实，并对此感到震惊和心痛，称稍后官方会发布声明。Chester昨天还在推特上转发了一条关于曼哈顿垃圾山的新闻。粉丝们纷纷在该推文下留言，不相信Chester已经走了。
外媒猜测，Chester选择在7月20日自杀的原因跟他极其要好的朋友、Soundgarden（声音花园）乐队以及Audioslave乐队主唱Chris Cornell有关，因为7月20日是Chris Cornell的诞辰。而Chris Cornell 于今年5月17日上吊自杀，享年52岁。Chris去世后，Chester还为他写下悼文。
对于Chester的自杀，亲友表示震惊但不意外，因为Chester曾经透露过想自杀的念头，他曾表示自己童年时被虐待，导致他医生无法走出阴影，也导致他长期酗酒和嗑药来疗伤。目前，洛杉矶警方仍在调查Chester的死因。
据悉，Chester与毒品和酒精斗争多年，年幼时期曾被成年男子性侵，导致常有轻生念头。Chester生前有过2段婚姻，育有6个孩子。
林肯公园在今年五月发行了新专辑《多一丝曙光One More Light》，成为他们第五张登顶Billboard排行榜的专辑。而昨晚刚刚发布新单《Talking To Myself》MV。"""
txt2 = """
近日，腾讯原副总裁吴军接受《头条有约》采访时表示，腾讯从来没有To B的基因。
吴军说道：“腾讯从来没有过ToB的基因。前些天还跟一些朋友讲就说他们，做云计算的就一直堵在人家企业门口，甚至主动给人家企业先打个一百万进去，说你把数据迁移到我这里。发现他整个企业做这种服务是完全跟不上的，没有这个基因，你不用想，就像恐龙想去冰河时代生活。腾讯是一个对社会真是没有危害的公司，但是你说要带给大家多少惊喜，微信之后的我也真说不出来。”
吴军称：“今天的谷歌，这是一个颇为平庸的公司。虽然它搞出了一些很亮眼的技术，但对人的帮助来讲，它远不像过去那么大。过去有它和没它，世界是不一样的。就是说它最后一个对人类最大的贡献是安卓。在这安卓以后，说它又贡献了什么了不得的东西，我也想不出来对人（类）有关。它的管理很混乱，最典型的就是它的云计算的策略，你可以看到，这中间的换人，权利的斗争等等这些东西，多少而且有点丑。谷歌之所以说有时候发展不行，跟这个CEO（桑达尔˙皮查伊）平庸也有很大的关系。”
吴军表示：“百度从七八年前起，其实基本上已经属于一个僵化的公司了，已经没有希望了。百度的二号人物永远是离职的。很多技术它都是起的大早，赶了个晚集。移动互联网时代它完全落伍了，可以讲完全不具有移动互联网的基因，所以做这种转变没有任何意义。说句不好听的，已经没有希望了。说句不好听的，陆奇都救不了它，没人救得了它。这家公司已经基本是不属于我们平时关注的对象了。”
吴军，原腾讯副总裁。吴军也是当前Google中日韩文搜索算法的主要设计者。著有《数学之美》、《浪潮之巅》和《文明之光》等畅销书。而吴军今天这样一番言论，有人认为说的好，很有道理，有人觉得吴军过于狂妄自大了。你们怎么看呢？";
"""


@pytest.mark.parametrize(("text", "rank"), [(txt, "sentence_rank"),
                                            (txt, "text_rank"),
                                            (txt, "sentence_similarity")])
def test_summarize(app, text, rank):
    with app.app_context():
        print(summarize(text, rank=rank, alpha=1.0))
