import requests
import time

data = {
    'userId': 'toan',
    'text': 'hello',
    'dateTime': time.time()
}
r = requests.post('http://127.0.0.1:5000/client/talktoai',
                  json=data,
                  timeout=10000000)

print(r)
print(r.json())