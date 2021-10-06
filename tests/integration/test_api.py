import urllib.request
import json


def test_post_req_api():
    url = 'http://127.0.0.1:8080/method/'
    post_data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd2"
                 "09a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments": {
            "phone": "79175002040",
            "email": "@",
            "first_name": "a",
            "last_name": "b",
            "birthday": "1.1.2000",
            "gender": 1
        }
    }
    json_data = json.dumps(post_data)
    req = urllib.request.Request(url, json_data.encode('utf-8'))
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header('Content-Length', str(len(json_data)))

    with urllib.request.urlopen(req) as resp:
        ans = resp.read()
        assert json.loads(ans) == {"response": {"score": 5.0}, "code": 200}