import pytest

from flaskr.chatbot_template_generator import Generator


@pytest.mark.parametrize(("template_path", "title", "length"), [
    (r"instance/chatbot_template.json", "公积金贷款", 200)
])
def test_generator(template_path, title, length):
    text = Generator(template_path)(title, length)
    print(text)
