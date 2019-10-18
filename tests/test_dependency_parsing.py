import pytest

from flaskr.extractor import *


@pytest.mark.parametrize("sentence", [
    '发现他整个企业做这种服务是完全跟不上的，没有这个基因，你不用想，就像恐龙想去冰河时代生活。',
    '我今天买了台iphone，这是我一个月的工资',
    '打电话回去查询，欧洲那边的答复是他们车都没有在发动机上印号码',
    '我刚把这个苹果咬了一口，你就把它抢走了',
    '林肯公园在今年五月发行了新专辑《多一丝曙光One More Light》，成为他们第五张登顶Billboard排行榜的专辑。'
])
def test_parse_sentence(sentence):
    res, trie = parse_sentence(sentence)
    for word in res.iterator():
        print(word)
    print('*' * 50)
    print(trie.NAME)
    queue = [trie]
    while len(queue) > 0:
        node = queue.pop()
        c = node.children.values()
        queue += c
        print((node.ID, node.LEMMA), [(w.ID, w.LEMMA) for w in c])


@pytest.mark.parametrize("sentence", [
    '近日，腾讯原副总裁吴军接受《头条有约》采访时表示：腾讯从来没有To B的基因。',
    '声明中指出，示威者于8月12及13日围堵机场的行为，已对香港国际机场的声誉和经济造成严重损害，更带来不可估量的损失。'
])
def test_build_sentence(sentence):
    _, trie = parse_sentence(sentence)
    print(build_sentence(trie))


@pytest.mark.parametrize("sentence", [
    '近日，腾讯原副总裁吴军接受《头条有约》采访时表示，腾讯从来没有To B的基因。',
    '一位路人告诉记者，“没人认出他们俩”。',
    '声明中指出，示威者于8月12及13日围堵机场的行为，已对香港国际机场的声誉和经济造成严重损害，更带来不可估量的损失。',
    '陈恒当地时间５日指出，对于许多分散在美东各州的乡亲来说，纽约因为便利生活而成为他们的“故乡”',
    '谷歌之所以说有时候发展不行，跟这个CEO（桑达尔˙皮查伊）平庸也有很大的关系。'
])
def test_parse_entity(say_words, sentence):
    _, trie = parse_sentence(sentence)
    for i in search_speck(trie, say_words):
        print(i)
