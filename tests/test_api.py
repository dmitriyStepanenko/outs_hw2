import api
import pytest
import hashlib


def get_hash(token: str):
    return hashlib.sha512(token.encode('utf-8')).hexdigest()


@pytest.mark.parametrize('account, login, token, arguments, method, answer', [
    ('a', 'b', get_hash('abOtus'), {}, '1', True),
    ('a', 'b', get_hash('abOtus1'), {}, '1', False),
])
def test_check_auth(account, login, token, arguments, method, answer):
    actual_answer = api.check_auth(
        request=api.MethodRequest(
            account=account,
            login=login,
            token=token,
            arguments=arguments,
            method=method
        )
    )
    assert actual_answer == answer



