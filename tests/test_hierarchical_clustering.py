import pytest

from flaskr.hierarchical_clustering import ClusterModel


@pytest.mark.parametrize("question", [
    "航空里程兑换比例"
])
def test_cluster(sif_model, question, k=3):
    cluster = ClusterModel(sif_model, r"instance/qa_corpus.csv", r"instance/qa_corpus_vec.txt")
    print(cluster(question, k=k))
