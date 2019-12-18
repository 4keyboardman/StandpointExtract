import pytest

from flaskr.boolean_search import SearchEngine
from flaskr.chatbot import dist_2_prob


@pytest.mark.parametrize(("source", "query"), [
    (r"instance/qa_corpus.csv", "公积金贷款")
])
def test_search_engine(source, query):
    se = SearchEngine(source)
    res = se(query)
    for i in res:
        print(i)
        print('*' * 50)
    dist_2_prob(res)
    print(res)
