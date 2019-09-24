import pytest

from flaskr.auto_summarizer import *


@pytest.mark.parametrize("text", ["""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。"""
                                  ])
def test_text_rank(text):
    sentences = cut_sentences(text)
    res = text_rank(sentences, allowPOS=('ns', 'n', 'vn', 'v'))
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


@pytest.mark.parametrize(("text", "rank"), [("""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。""", "text_rank"),
                                            ("""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。""", "sentence_similarity")
                                            ]
                         )
def test_summarize(app, text, rank):
    with app.app_context():
        print(summarize(text, rank=rank))
