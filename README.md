Домашнее задание/проектная работа выполнено (-на) для курса [Python Developer. Professional](https://otus.ru/lessons/python-professional/?int_source=courses_catalog&int_term=programming)

# Scoring API

API необычно тем, что пользователи дергают методы POST запросами. 
Чтобы получить результат пользователь отправляет в POST запросе валидный JSON определенного формата на локейшн /method.

### Структура запроса
```
{
    "account": "<имя компании партнера>", 
    "login": "<имя пользователя>", 
    "method": "<имя метода>", 
    "token": "<аутентификационный токен>", 
    "arguments": {"<словарь с аргументами вызываемого метода>"}
}
```
### Структура ответа
```
{"code": <числовой код>, "response": {<ответ вызываемого метода>}}
```

### Доступные методы

#### online_score

пример
```
curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method":"online_score", "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95","arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав", "last_name":"Ступников", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/
```
#### clients_interests
пример
```
curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", "method":"clients_interests", "token":"d3573aff1555cd67dccf21b95fe8c4dc8732f33fd4e32461b7fe6a71d83c947688515e36774c00fb630b039fe2223c991f045f13f240913860502 "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' http://127.0.0.1:8080/method/
```

## Запуск API
```
python api.py
```


## Запуск тестов
```
python -m unittest tests/test.py
```
