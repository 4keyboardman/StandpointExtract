import pytest

from flaskr.view_extract_sif import *


@pytest.mark.parametrize("text", [
    "这位售货员说，进入6月份，猪肉价格一直呈上涨的趋势，目前的猪肉价格为近两个月的高点。猪肉进价在蹭蹭上涨，但零售价他们却不敢随便涨，“现在都卖不动了。”"
])
def test_extract(say_words, sif_model, text):
    print(extract(text, say_words, sif_model))


@pytest.mark.parametrize("text", [
    "这位售货员说，进入6月份，猪肉价格一直呈上涨的趋势，目前的猪肉价格为近两个月的高点。猪肉进价在蹭蹭上涨，但零售价他们却不敢随便涨，“现在都卖不动了。”"
])
def test_parse_sentence(text):
    print(parse_sentence(text))


@pytest.mark.parametrize("sentence", [
    "这位售货员说，进入6月份，猪肉价格一直呈上涨的趋势，目前的猪肉价格为近两个月的高点。猪肉进价在蹭蹭上涨，但零售价他们却不敢随便涨，“现在都卖不动了。”",
    "进入6月份，猪肉价格一直呈上涨的趋势，目前的猪肉价格为近两个月的高点。"
])
@pytest.mark.parametrize("related_words", [
    "说", "说"
])
def test_search_dependency(sentence, related_words):
    print(search_dependency(sentence, related_words))
