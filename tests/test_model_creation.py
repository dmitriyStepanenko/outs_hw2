import api
import pytest


def test_base_field_invalid_creating_empty():
    class A:
        field = api.BaseField(required=True, nullable=False)

        def __init__(self, field=None):
            self.field = field

    try:
        A()
    except ValueError as e:
        assert str(e) == 'Поле field должно быть обязательно заполнено'


def test_base_field_invalid_creating_null():
    class A:
        field = api.BaseField(required=True, nullable=False)

        def __init__(self, field=None):
            self.field = field

    try:
        A('')
    except ValueError as e:
        assert str(e) == 'Поле field должно быть не пусто'


@pytest.mark.parametrize('required, nullable, value', [
    (True, True, ''),
    (False, False, None),
    (False, True, None),
    (False, True, ''),
    (True, False, -1),
    (True, False, '1')
])
def test_base_field_ok_creating(required, nullable, value):
    class A:
        field = api.BaseField(required=required, nullable=nullable)

        def __init__(self, field=None):
            self.field = field

    a = A(value)
    assert a.field == value


@pytest.mark.parametrize('value, error, type_field', [
    # api.CharField
    (1, 'field должен быть строкой', api.CharField),
    ({}, 'field должен быть строкой', api.CharField),
    ([], 'field должен быть строкой', api.CharField),

    # api.EmailField
    ('1', 'Email должен содержать @', api.EmailField),
    ('aaa.com', 'Email должен содержать @', api.EmailField),
    (1, 'field должен быть строкой', api.EmailField),

    # api.PhoneField
    ('1', 'Телефон должен начинаться с 7', api.PhoneField),
    (89991112223, 'Телефон должен начинаться с 7', api.PhoneField),
    ('7aaa.com', 'Телефон должен содержать 11 цифр', api.PhoneField),
    (777777777788888888, 'Телефон должен содержать 11 цифр', api.PhoneField),
    (1.2, 'Телефон должен быть или строкой или числом', api.PhoneField),
    ([7, 4], 'Телефон должен быть или строкой или числом', api.PhoneField),

    # api.DateField
    (1, 'field должен быть строкой', api.DateField),
    ('aaa.com', "time data 'aaa.com' does not match format '%d.%m.%Y'", api.DateField),
    ('1-2-2020', "time data '1-2-2020' does not match format '%d.%m.%Y'", api.DateField),

    # api.BirthDayField
    (1, 'field должен быть строкой', api.BirthDayField),
    ('aaa.com', "time data 'aaa.com' does not match format '%d.%m.%Y'", api.BirthDayField),
    ('1-2-2020', "time data '1-2-2020' does not match format '%d.%m.%Y'", api.BirthDayField),
    ('1.1.0001', 'Дата дня рождения должна быть не больше 70 лет назад', api.BirthDayField),

    # api.GenderField
    ('male', 'Гендер должен быть числом', api.GenderField),
    ('1', 'Гендер должен быть числом', api.GenderField),
    (5, 'Значение гендера должно быть 0, 1 или 2', api.GenderField),
    (-1, 'Значение гендера должно быть 0, 1 или 2', api.GenderField),

    # api.ClientIDsField
    (1, 'ClientIDs должен быть списком', api.ClientIDsField),
    ({1, 2}, 'ClientIDs должен быть списком', api.ClientIDsField),
    (['1', '1'], 'в списке ClientIDs должны быть только числа', api.ClientIDsField),
    ([1, '1'], 'в списке ClientIDs должны быть только числа', api.ClientIDsField),
])
def test_fields_invalid_creating(value, error, type_field):
    class A:
        field = type_field(required=True, nullable=True)

        def __init__(self, field=None):
            self.field = field

    try:
        A(value)
    except ValueError as e:
        assert str(e) == error


@pytest.mark.parametrize('value, field_type', [
    # api.CharField
    ('1', api.CharField),
    ('', api.CharField),
    ('aaa', api.CharField),

    # api.EmailField
    ('@', api.EmailField),
    ('aaa@.com', api.EmailField),
    ('1@1', api.EmailField),

    # api.PhoneField
    ('71112223334', api.PhoneField),
    (74321432143, api.PhoneField),

    # api.DateField
    ('1.2.2000', api.DateField),
    ('1.1.0001', api.DateField),

    # api.BirthDayField
    ('1.2.2000', api.BirthDayField),

    # api.GenderField
    (0, api.GenderField),
    (1, api.GenderField),
    (2, api.GenderField),

    # api.ClientIDsField
    ([0], api.ClientIDsField),
    ([0, 0], api.ClientIDsField),
])
def test_fields_ok_creating(value, field_type):
    class A:
        field = field_type(required=True, nullable=True)

        def __init__(self, field=None):
            self.field = field

    a = A(value)
    assert a.field == value


def test_creating_class_without_init():
    class A(api.Structure):
        field1 = api.BaseField(required=True, nullable=True)
        field2 = api.BaseField(required=True, nullable=False)

    a = A('', 1)

    assert a.field1 == ''
    assert a.field2 == 1


@pytest.mark.parametrize('params', [
    {'client_ids': [1], 'date': '1.1.1000'},
    {'client_ids': [1, 2]},
])
def test_client_interests_ok_creating(params):
    cli_req = api.ClientsInterestsRequest(**params)

    for key, val in params.items():
        assert getattr(cli_req, key) == val


@pytest.mark.parametrize('params, error', [
    ({}, 'Поле client_ids должно быть обязательно заполнено'),
    ({'client_ids': 1, 'date': '1.1.1000'}, 'ClientIDs должен быть списком'),
    ({'date': '1.1.1000'}, 'Поле client_ids должно быть обязательно заполнено'),
])
def test_client_interests_invalid_creating(params, error):
    try:
        api.ClientsInterestsRequest(**params)

    except ValueError as e:
        assert str(e) == error


@pytest.mark.parametrize('params', [
    {'first_name': 'a', 'last_name': 'b',
     'email': 'a@b.com', 'phone': 77_777_777_777,
     'birthday': '1.2.2000', 'gender': 1},
    {'first_name': '', 'email': '', 'birthday': ''},
    {'first_name': '', 'last_name': ''},
    {'phone': '77777777777', 'gender': 0},
    {}
])
def test_online_score_ok_creating(params):
    cli_req = api.OnlineScoreRequest(**params)

    for key, val in params.items():
        assert getattr(cli_req, key) == val


@pytest.mark.parametrize('params, error', [
    ({}, 'Поле client_ids должно быть обязательно заполнено'),
    ({'client_ids': 1, 'date': '1.1.1000'}, 'ClientIDs должен быть списком'),
    ({'date': '1.1.1000'}, 'Поле client_ids должно быть обязательно заполнено'),
])
def test_online_score_invalid_creating(params, error):
    try:
        api.OnlineScoreRequest(**params)

    except ValueError as e:
        assert str(e) == error


@pytest.mark.parametrize('params', [
    {'first_name': 'a', 'last_name': 'b',
      'email': 'a@b.com', 'phone': 77_777_777_777,
      'birthday': '1.2.2000', 'gender': 1},
    {'first_name': '', 'email': '', 'birthday': ''},
    {'first_name': '', 'last_name': ''},
    {'phone': '77777777777', 'gender': 0},
    {},
    {'phone': '77777777777', 'email': ''},
    {'birthday': '1.5.2039', 'gender': 0},
])
def test_online_score_validate(params):
    cli_req = api.OnlineScoreRequest(**params)

    try:
        assert cli_req.validate() is None
    except ValueError as e:
        assert str(e) == 'Не валидный запрос'


@pytest.mark.parametrize('params', [
    {'account': 'a', 'login': 'b', 'token': '1', 'arguments': {}, 'method': 'a'},
    {'login': 'b', 'token': '1', 'arguments': {}, 'method': 'a'},
    {'account': '', 'login': '', 'token': '1', 'arguments': {'a': 'b'}, 'method': 'a'},
])
def test_method_request_ok_creating(params):
    cli_req = api.MethodRequest(**params)

    for key, val in params.items():
        assert getattr(cli_req, key) == val


@pytest.mark.parametrize('params, error', [
    ({'account': 'a', 'token': '1', 'arguments': {}, 'method': ''}, 'Поле login должно быть обязательно заполнено'),
    ({'login': 'b', 'token': '1', 'arguments': {}, 'method': ''}, 'Поле method должно быть не пусто'),
    ({'account': '', 'login': '', 'token': 1, 'arguments': {'a': 'b'}, 'method': 'a'}, 'token должен быть строкой'),
])
def test_method_request_invalid_creating(params, error):
    try:
        api.MethodRequest(**params)
    except ValueError as e:
        assert str(e) == error
