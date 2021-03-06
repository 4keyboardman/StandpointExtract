import pytest

from flaskr.nlp_model import get_related_words


@pytest.mark.parametrize("initial_words", [["那边"]])
def test_get_related_words(word2vec_model, initial_words):
    print(get_related_words(initial_words, word2vec_model))
