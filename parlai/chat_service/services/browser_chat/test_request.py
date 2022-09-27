import requests
import time

data = {
    'userId': 'moses',
    'text': "moses 1",
    'dateTime': time.time()
}

start = time.time()
r = requests.post('http://127.0.0.1:5000/client/talktoai',
                  json=data,
                  timeout=10000000)

print(r)
print(r.json())
stop = time.time()
print(stop - start)

data = {
    'userId': 'moses',
    'text': "moses 2",
    'dateTime': time.time()
}

start = time.time()
r = requests.post('http://127.0.0.1:5000/client/talktoai',
                  json=data,
                  timeout=10000000)

print(r)
print(r.json())
stop = time.time()
print(stop - start)

data = {
    'userId': 'toan',
    'text': "toan 1",
    'dateTime': time.time()
}

start = time.time()
r = requests.post('http://127.0.0.1:5000/client/talktoai',
                  json=data,
                  timeout=10000000)

print(r)
print(r.json())
stop = time.time()
print(stop - start)

data = {
    'userId': 'toan',
    'text': "toan 2",
    'dateTime': time.time()
}

start = time.time()
r = requests.post('http://127.0.0.1:5000/client/talktoai',
                  json=data,
                  timeout=10000000)

print(r)
print(r.json())
stop = time.time()
print(stop - start)


data = {
    'userId': 'moses',
    'dataNumber': 20
}
r = requests.get('http://127.0.0.1:5000/client/retrievehistory',
                 json=data)