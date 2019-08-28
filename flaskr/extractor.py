from flaskr.SIF_embedding import SIFModel
from flaskr.speck_classifier import BiRNN
from flaskr import view_extract_sif, view_extract_rnn


class Extractor:

    def extract(self, text: str) -> [['entity', 'standpoint']]:
        """
        根据文本提取人物言论
        :param text:
        :return:
        """
        raise NotImplementedError


class SIFExtractor(Extractor):

    def __init__(self, sif_model: SIFModel, say_words):
        self.sif_model = sif_model
        self.say_words = say_words

    def extract(self, text):
        return view_extract_sif.extract(text, self.say_words, self.sif_model)


class RNNExtractor(Extractor):

    def __init__(self, rnn_model: BiRNN, say_words):
        self.say_words = say_words
        self.rnn_model = rnn_model

    def extract(self, text):
        return view_extract_rnn.extract(self.say_words, self.rnn_model)