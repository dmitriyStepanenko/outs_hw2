import scoring
import pytest
from datetime import datetime


@pytest.mark.parametrize('phone, email, birthday, gender, first_name, last_name, answer', [
    ('77777777777', 'a@b', datetime(2000, 1, 1), 1, 'a', 'b', 5),
    ('77777777777', 'a@b', datetime(2000, 1, 1), 0, 'a', 'b', 3.5),
    ('77777777777', 'a@b', datetime(2000, 1, 1), 1, '', 'b', 4.5),
    ('77777777777', 'a@b', None, None, None, None, 3),
    ('77777777777', 'a@b', None, 1, 'aa', 'b', 4),
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


@pytest.mark.parametrize('cid, answer', [
    (1, ['a', 'b']),
    (2, [])
])
def test_get_interests(store, cid, answer):
    interests = scoring.get_interests(store, cid)

    assert interests == answer
