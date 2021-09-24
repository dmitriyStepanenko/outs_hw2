#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
from datetime import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Tuple
from weakref import WeakKeyDictionary
import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
METHOD_ONLINE_SCORE = 'online_score'
METHOD_CLIENTS_INTERESTS = 'clients_interests'


class BaseField:
    def __init__(self, required: bool, nullable: bool):
        self._is_nullable = nullable
        self._is_required = required
        self.data = WeakKeyDictionary()

    def __set__(self, instance, value):
        if self._is_required and value is None:
            raise ValueError(f'Поле {instance} должно быть обязательно заполнено')
        if value is not None:
            self.validate(instance, value)
            self.data[instance] = value

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def validate(self, instance, value):
        if not self._is_nullable and not value:
            raise ValueError(f'Поле {instance} должно быть не пусто')


class CharField(BaseField):
    def validate(self, instance, value):
        super(CharField, self).validate(instance, value)
        if not isinstance(value, str):
            raise ValueError(f'{instance} должен быть строкой')


class ArgumentsField(BaseField):
    pass


class EmailField(CharField):
    def validate(self, instance, value):
        super(EmailField, self).validate(instance, value)
        if value.find('@') == -1:
            raise ValueError('Email должен содержать @')


class PhoneField(BaseField):
    def validate(self, instance, value):
        super(PhoneField, self).validate(instance, value)
        if not (isinstance(value, str) or isinstance(value, int)):
            raise ValueError('Телефон должен быть или строкой или числом')
        str_value = str(value)
        if str_value[0] != '7':
            raise ValueError('Телефон должен начинаться с 7')
        if len(str_value) != 11:
            raise ValueError('Телефон должен содержать 11 цифр')


class DateField(CharField):
    def validate(self, instance, value):
        super(DateField, self).validate(instance, value)
        datetime.strptime(value, '%d.%m.%Y')


class BirthDayField(CharField):
    def validate(self, instance, value):
        super(BirthDayField, self).validate(instance, value)

        if (datetime.now() - datetime.strptime(value, '%d.%m.%Y')).days > 70 * 365:
            raise ValueError('Дата дня рождения должна быть не больше 70 лет назад')


class GenderField(BaseField):
    def validate(self, instance, value):
        if not isinstance(value, int):
            raise ValueError('Гендер должен быть числом')

        if value not in list(GENDERS.keys()):
            raise ValueError('Значение гендера должно быть 0, 1 или 2')


class ClientIDsField(BaseField):
    def validate(self, instance, value):
        super(ClientIDsField, self).validate(instance, value)

        if not isinstance(value, list):
            raise ValueError('ClientIDs должен быть списком')

        for d in value:
            if not (isinstance(d, int) or isinstance(d, float)):
                raise ValueError('в списке ClientIDs должны быть только числа')


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def __init__(self, client_ids=None, date=None):
        self.date = date
        self.client_ids = client_ids


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, first_name=None, last_name=None, email=None, phone=None, birthday=None, gender=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birthday = birthday
        self.gender = gender

        if not (self.email and self.phone or
                self.gender is not None and self.birthday or
                self.first_name and self.last_name):
            raise ValueError('Не валидный запрос')


class MethodRequest(object):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, account=None, login=None, token=None, arguments=None, method=None, header=None):
        self.account = account
        self.login = login
        self.token = token
        self.arguments = arguments
        self.method = method

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest_str = datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
    else:
        digest_str = request.account + request.login + SALT
    digest = hashlib.sha512(digest_str.encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    logging.info(digest)
    logging.info(request.token)
    return False


def method_handler(request: Dict, ctx, store) -> Tuple[Dict, int]:
    """
    :return: response, code
    """
    if len(request['body']) == 0:
        return {"code": INVALID_REQUEST, "error": ERRORS[INVALID_REQUEST]}, INVALID_REQUEST
    try:
        method_request = MethodRequest(**request['body'])
        if not check_auth(method_request):
            return {"code": FORBIDDEN, "error": ERRORS[FORBIDDEN]}, FORBIDDEN

        if method_request.method == METHOD_ONLINE_SCORE:
            online_req = OnlineScoreRequest(**method_request.arguments)
            ctx['has'] = method_request.arguments.keys()
            score = scoring.get_score(
                store=store,
                phone=online_req.phone,
                email=online_req.email,
                birthday=online_req.birthday,
                gender=online_req.gender,
                first_name=online_req.first_name,
                last_name=online_req.last_name,
            ) if not method_request.is_admin else 42
            return {"score": score}, OK

        if method_request.method == METHOD_CLIENTS_INTERESTS:
            client_req = ClientsInterestsRequest(**method_request.arguments)
            ctx['nclients'] = len(client_req.client_ids)
            interests = {}
            for client_id in client_req.client_ids:
                interests[client_id] = scoring.get_interests(store, cid=client_id)
            return interests, OK

    except Exception as e:
        logging.exception(e)
        return {"code": INVALID_REQUEST, "error": ERRORS[INVALID_REQUEST]}, INVALID_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        data_string = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf-8'))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
