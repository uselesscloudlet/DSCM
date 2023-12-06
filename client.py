import requests

url = "http://127.0.0.1:80/check_number"
while True:
    number = int(input())
    payload = {"number": number}
    response = requests.post(url, json=payload)
    print(response.json())