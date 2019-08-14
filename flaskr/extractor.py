from flask import current_app
from flaskr import view_extract


def extract(text: str) -> [['entity', 'standpoint']]:
    """
    根据文本提取人物言论
    :param text:
    :return:
    """
    return view_extract.extract(text, current_app.word_model)


