import time

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


@pytest.mark.parametrize('key, value, s_time', [
    ('1', 1, 100),
    ('2', 2, 1000),
    (1, 1, 100),
    ('2', 2, '1000'),
])
def test_cache_setting_ok(storage, key, value, s_time):
    storage.cache_set(key, value, s_time)
    assert storage._cache[key].value == value


@pytest.mark.parametrize('key, value, s_time, error', [
    (None, -1, -1, "Invalid input of type: 'NoneType'. Convert to a bytes, string, int or float first."),
    ('1', -1, -1, 'invalid expire time in setex'),
])
def test_cache_setting_wrong(storage, key, value, s_time, error):
    try:
        storage.cache_set(key, value, s_time)
    except Exception as e:
        assert str(e) == error


def test_cache_getting(storage):
    storage.cache_set('1', 1.5, 1)
    assert float(storage.cache_get('1')) == 1.5
    time.sleep(2)
    assert storage.cache_get('1') is None
