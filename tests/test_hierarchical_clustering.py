import pytest

from flaskr.hierarchical_clustering import ClusterModel
from flaskr.chatbot import dist_2_prob


@pytest.mark.parametrize("question", [
    "航空里程兑换比例"
])
def test_cluster(sif_model, question, k=3):
    cluster = ClusterModel(sif_model, r"instance/qa_corpus.csv", r"instance/qa_corpus_vec.txt")
    res = cluster(question, k=k)
    for i in res:
        print(i)
        print('*' * 50)
    res = dist_2_prob(res)
    print(res)
