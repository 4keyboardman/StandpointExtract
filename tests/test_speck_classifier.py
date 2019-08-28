import pytest
from flaskr.speck_classifier import *


@pytest.mark.parametrize("source", [r'instance/vocabulary.txt'])
def test_load_vocabulary(source):
    counter = load_vocabulary(source)
    print(counter['的'])


@pytest.mark.parametrize("sentence", [
    '这是 今天 看到 的 最 欢乐 的 微博 了',
    '该 政策 将 于 月 日 正式 实施',
    '近日，腾讯原副总裁吴军接受《头条有约》采访时表示：腾讯从来没有To B的基因。',
    '腾讯从来没有To B的基因。',
    '吴军，原腾讯副总裁。',
    '吴军也是当前Google中日韩文搜索算法的主要设计者。著有《数学之美》、《浪潮之巅》和《文明之光》等畅销书。',
    '而吴军今天这样一番言论，有人认为说的好，很有道理，有人觉得吴军过于狂妄自大了。你们怎么看呢？'
])
def test_model(rnn_net, sentence):
    print(sentence, rnn_net.predict(sentence))