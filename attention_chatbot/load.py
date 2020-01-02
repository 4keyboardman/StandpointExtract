import torch
import re
import os
import unicodedata

from .config import MAX_LENGTH, save_dir
import argparse

SOS_token = 0
EOS_token = 1
PAD_token = 2


class Voc:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS", 2: "PAD"}
        self.n_words = 3  # Count SOS and EOS

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1

    def trim(self, min_count):
        """
        删除低于特定计数阈值的单词
        """
        if self.trimmed:
            return
        self.trimmed = True
        keep_words = []
        for k, v in self.word2count.items():
            if v >= min_count:
                keep_words.append(k)
        print('keep_words {} / {} = {:.4f}'.format(
            len(keep_words), len(self.word2index), len(keep_words) / len(self.word2index)
        ))
        # 重初始化字典
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token: "PAD", SOS_token: "SOS", EOS_token: "EOS"}
        self.num_words = 3  # Count default tokens
        for word in keep_words:
            self.addWord(word)


def unicodeToAscii(s):
    """
    将Unicode字符串转换为纯ASCII
    Turn a Unicode string to plain ASCII, thanks to
    http://stackoverflow.com/a/518232/2809427
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def normalizeString(s):
    """
    Lowercase, trim, and remove non-letter characters     
    """
    s = unicodeToAscii(s.lower().strip())
    s = re.sub(r"([.!?])", r" \1", s)
    s = re.sub(r"[^a-zA-Z.!?]+", r" ", s)
    s = re.sub(r"\s+", r" ", s).strip()
    return s


def readVocs(corpus, corpus_name):
    """
    初始化Voc对象 和 格式化pairs对话存放到list中
    """
    print("Reading lines...")

    # combine every two lines into pairs and normalize
    with open(corpus) as f:
        content = f.readlines()
    # import gzip
    # content = gzip.open(corpus, 'rt')
    lines = [x.strip() for x in content]
    it = iter(lines)
    # pairs = [[normalizeString(x), normalizeString(next(it))] for x in it]
    pairs = [[x, next(it)] for x in it]

    voc = Voc(corpus_name)
    return voc, pairs


def filterPair(p):
    # 如果对 'p' 中的两个句子都低于 MAX_LENGTH 阈值，则返回True
    # input sequences need to preserve the last word for EOS_token
    return len(p[0].split(' ')) < MAX_LENGTH and \
        len(p[1].split(' ')) < MAX_LENGTH


def filterPairs(pairs):
    # 过滤满足条件的 pairs 对话
    return [pair for pair in pairs if filterPair(pair)]


def prepareData(corpus, corpus_name):
    # 使用上面定义的函数，返回一个填充的voc对象和对列表
    print("Start preparing training data ...")
    voc, pairs = readVocs(corpus, corpus_name)
    print("Read {!s} sentence pairs".format(len(pairs)))
    pairs = filterPairs(pairs)
    print("Trimmed to {!s} sentence pairs".format(len(pairs)))
    print("Counting words...")
    for pair in pairs:
        voc.addSentence(pair[0])
        voc.addSentence(pair[1])
    print("Counted words:", voc.n_words)
    directory = os.path.join(save_dir, 'training_data', corpus_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    torch.save(voc, os.path.join(directory, '{!s}.tar'.format('voc')))
    torch.save(pairs, os.path.join(directory, '{!s}.tar'.format('pairs')))
    return voc, pairs


def loadPrepareData(corpus):
    corpus_name = corpus.split('/')[-1].split('.')[0]
    try:
        print("Start loading training data ...")
        voc = torch.load(os.path.join(save_dir, 'training_data', corpus_name, 'voc.tar'))
        pairs = torch.load(os.path.join(save_dir, 'training_data', corpus_name, 'pairs.tar'))
    except FileNotFoundError:
        print("Saved data not found, start preparing trianing data ...")
        voc, pairs = prepareData(corpus, corpus_name)
    return voc, pairs


def trimRareWords(voc, pairs, MIN_COUNT=3):
    """
    另一种有利于让训练更快收敛的策略是去除词汇表中很少使用的单词。减少特征空间也会降低模型学习目标函数的难度。
    我们通过以下两个步 骤完成这个操作:
    * 使用voc.trim函数去除 MIN_COUNT 阈值以下单词 。
    * 如果句子中包含词频过小的单词，那么整个句子也被过滤掉。
    """
    # 修剪来自voc的MIN_COUNT下使用的单词
    voc.trim(MIN_COUNT)
    # Filter out pairs with trimmed words
    keep_pairs = []
    for pair in pairs:
        input_sentence = pair[0]
        output_sentence = pair[1]
        keep_input = True
        keep_output = True
        # 检查输入句子
        for word in input_sentence.split(' '):
            if word not in voc.word2index:
                keep_input = False
                break
        # 检查输出句子
        for word in output_sentence.split(' '):
            if word not in voc.word2index:
                keep_output = False
                break
        # 只保留输入或输出句子中不包含修剪单词的对
        if keep_input and keep_output:
            keep_pairs.append(pair)
    print("Trimmed from {} pairs to {}, {:.4f} of total".format(len(pairs), len(keep_pairs), len(keep_pairs) / len(pairs)))
    return keep_pairs


def main():
    parser = argparse.ArgumentParser(description='加载和清洗数据')
    parser.add_argument('-i', '--input', required=True, help='语料库文件夹路径')
    args = parser.parse_args()
    vargs = vars(args)
    print("\nArguments:")
    for arg in vargs:
        print("{}={}".format(arg, getattr(args, arg)))
    voc, pairs = loadPrepareData(args.input)
    # 打印一些对进行验证
    print("\npairs:")
    for pair in pairs[:10]:
        print(pair)


if __name__ == "__main__":
    main()
