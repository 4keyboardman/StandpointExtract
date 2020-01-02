import pytest


@pytest.mark.parametrize("sentence", [
    'do you listen to this crap?',
    'Where did he go?'
])
def test_chatbot(attention_chatbot, sentence):
    print(attention_chatbot(sentence))
