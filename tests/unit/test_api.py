import json
import uuid
from datetime import datetime
import random

import api
import pytest
import hashlib


def get_hash(token: str):
    return hashlib.sha512(token.encode('utf-8')).hexdigest()


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        msg = datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
    request["token"] = hashlib.sha512(msg.encode('utf-8')).hexdigest()


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


@pytest.mark.parametrize('req, ans_code', [
    ({}, 422),
    ({'body': {}}, 422),
    ({'body': {"account": "a", "login": "b", "method": "o", "token": "", "arguments": {}}}, 403),
    ({'body': {"account": "a", "login": "b", "method": "o", "token": "1", "arguments": {}}}, 403),
    ({'body': {"account": "a", "login": "admin", "method": "a", "token": "", "arguments": {}}}, 403),
])
def test_invalid_method_handler(req, ans_code):
    response, code = api.method_handler(req, {}, None)
    assert code == ans_code
    assert response is None


@pytest.mark.parametrize('req_body', [
    {"account": "a", "login": "b", "method": "o", "token": "", "arguments": {}},
    {"account": "a", "login": "admin", "method": "a", "token": "", "arguments": {}},
    {"account": "a", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    {"account": "a", "login": "admin", "method": "online_score", "token": "", "arguments": {"a": 1}},
])
def test_invalid_body_method_handler(req_body):
    set_valid_auth(req_body)
    response, code = api.method_handler({'body': req_body}, {}, None)
    assert code == api.INVALID_REQUEST
    assert response is None


@pytest.mark.parametrize('arguments', [
    {},
    {"phone": "", "email": "", "gender": "", "birthday": "", "first_name": "", "last_name": ""},
])
def test_invalid_online_score_handling(arguments):
    req_body = {"account": "a", "login": "b", "method": "o", "token": "", "arguments": arguments}
    set_valid_auth(req_body)
    response, code = api.method_handler({'body': req_body}, {}, None)
    assert code == api.INVALID_REQUEST
    assert response is None


@pytest.mark.parametrize('arguments, score', [
    ({"phone": 77_777_777_788, "email": "@"}, 3.),

    ({"phone": '77777777777', "email": 'a@b',
      "birthday": '1.2.2000', "gender": 1, "first_name": 'a', "last_name": 'b'}, 5.)
])
def test_get_online_score(store, arguments: dict, score):
    mr = api.MethodRequest(arguments=arguments)
    ctx = {}
    res = api.get_online_score(mr, ctx, store)
    assert res == ({'score': score}, api.OK)
    assert ctx == {'has': list(arguments.keys())}


@pytest.mark.parametrize('arguments, ans', [
    ({"client_ids": [3, 2], "date": "4.3.2011"}, {3: ['a', 'f'], 2: []}),
    ({"client_ids": [3], "date": "4.3.2011"}, {3: ['a', 'f']}),
])
def test_get_client_interests(store, arguments: dict, ans):
    store.cache["i:3"] = json.dumps(['a', 'f'])
    mr = api.MethodRequest(arguments=arguments)
    ctx = {}
    res = api.get_client_interests(mr, ctx, store)
    assert res == (ans, api.OK)
    assert ctx == {'nclients': len(ans)}


def test_main_http_handler_get_req_id():
    rd = random.Random()
    rd.seed(0)
    uid_val = rd.getrandbits(128)
    uuid.uuid4 = lambda: uuid.UUID(int=uid_val)

    assert api.MainHTTPHandler.get_request_id({'HTTP_X_REQUEST_ID': '123'}) == '123'
    assert api.MainHTTPHandler.get_request_id({}) == uuid.UUID(int=uid_val).hex
