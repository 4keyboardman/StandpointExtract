import pytest

from flaskr.utils import cosine_similarity


@pytest.mark.parametrize(("x", "y"), [
    ([1, 2, 3], [4, 5, 6])
])
def test_cosine_similarity(x, y):
    print(cosine_similarity(x, y))
