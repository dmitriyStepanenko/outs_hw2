import scoring
import pytest


@pytest.fixture
def store():
    class Store:
        def __init__(self, cache: dict = None):
            self.cache = cache if cache else {}

        def get(self, name):
            return self.cache.get(name)

        def catch_get(self, name):
            return self.get(name)

        def set(self, name, value):
            self.cache[name] = value

        def cache_set(self, name, value, time):
            self.set(name, value)

    return Store()


@pytest.mark.parametrize('phone, email, birthday, gender, first_name, last_name, answer', [
    (77_777_777_777, 'a@b', '1.2.2000', 0, 'a', 'b', 5),
])
def test_get_score(store, phone, email, birthday, gender, first_name, last_name, answer):
    score = scoring.get_score(
        store=store,
        phone=phone,
        email=email,
        birthday=birthday,
        gender=gender,
        first_name=first_name,
        last_name=last_name)

    assert score == answer
