import pytest


@pytest.mark.parametrize("text", ["""生成摘要的主要思想是找到包含整个数据集“信息”的数据子集。这种技术在当今行业内被广泛使用。搜索引擎就是一个例子; 
        其他还包括文档摘要生成，图像收集和视频处理。文档摘要生成算法试图通过查找信息量最大的句子来创建整个文档的代表性摘要，而在图像摘要中，
        计算机则试图找到最具代表性的显著的图像。对于监控视频，人们可能希望从平静的环境影像中提取出重要事件。"""
                                  ])
def test_auto_summarize(client, text):
    response = client.post("/auto_summarizer", data={"test": text})
    print(response)
