import requests
import time

data = {
    'userId': 'moses',
    'text': "hello, what is your name? How come you floatting around?",
    'dateTime': time.time()
}

start = time.time()
r = requests.post('http://127.0.0.1:5000/client/talktoai',
                  json=data,
                  timeout=10000000)

# data = {
#     'userId': 'toan',
#     'dataNumber': 20
# }
# r = requests.get('http://127.0.0.1:5000/client/retrievehistory',
#                  json=data)

print(r)
print(r.json())
stop = time.time()
print(stop - start)