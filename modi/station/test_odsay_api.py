import requests

url = "https://api.odsay.com/v1/api/searchPubTransPathT"
params = {
    "apiKey": "/A4oSsOdNvZlNpw4iYxt3WyqMYHQ0xIy0F6qhsOvGqg",
    "SX": 127.025509,
    "SY": 37.637885,
    "EX": 127.017126,
    "EY": 37.592968,
}

res = requests.get(url, params=params)
print(res.status_code)   # 200이면 성공
print(res.json())        # 실제 응답 확인