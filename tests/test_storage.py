import datetime

import pytest
from store import Storage


@pytest.fixture
def storage():
    return Storage()


def test_setting(storage):
    storage.set('123', 345)

    assert int(storage.get('123')) == 345


def test_getting(storage):
    assert storage.get('12345') is None


@pytest.mark.parametrize('key, value, time', [
    ('1', 1, 100),
    ('2', 2, 1000),
])
def test_cache_setting_ok(storage, key, value, time):
    storage.cache_set(key, value, time)
    assert storage._cache[key].value == value


@pytest.mark.parametrize('key, value, time', [
    (1, 1, 100),
    ('2', 2, '1000'),
    (None, -1, -1)
])
def test_cache_setting_wrong(storage, key, value, time):
    storage.cache_set(key, value, time)
    assert storage._cache[key].value == value


def test_cache_getting():
    ...
