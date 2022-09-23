from flask import Flask, redirect, url_for, request, g
import requests
import socket
import time
from subprocess import Popen, PIPE 
from parlai.chat_service.services.browser_chat.aws_transcribe import transcribe_file
from parlai.chat_service.services.browser_chat.aws_polly import get_voice

app = Flask(__name__)
active_userid_port = {}

def get_unused_port():
    """
    Get an empty port for the Pyro nameservr by opening a socket on random port,
    getting port number, and closing it [not atomic, so race condition is possible...]
    Might be better to open with port 0 (random) and then figure out what port it used.
    """
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.bind(('localhost', 0))
    _, port = so.getsockname()
    so.close()
    return port

@app.route('/client_chat', methods = ['POST'])
def client_chat():
    if 'voice' in request.json:
        print(request.json['voice'])
        text = transcribe_file(request.json['voice'])
    else:
        text = request.json['text']
    userid = request.json['userid']
    if not active_userid_port.get(userid, None):
        port = get_unused_port()
        print(port)
        Popen(['python', 'client.py', '--port', '10002', '--serving-port', str(port)])
        #create_client(port=10002, serving_port=port)
        active_userid_port[userid] = port
        time.sleep(1)
        #return {'status': 'connected'}
    else:
        port = active_userid_port[userid]

    try:
        r = requests.post(f"http://localhost:{port}/interact",
                            json={'text': f'{text}'},
                            timeout=10000000)
    except requests.exceptions.ConnectionError:
        return {"status": f"close session with {userid}"}
    result = {}
    result['text'] = r.json()['text']
    if result['text'] == '.-.beep. ...-boop. -.beep--. .':
        result['voice'] = None
    else:
        result['voice'] = get_voice(result['text'])
    print(result)
    return result
    
@app.route('/client_close', methods = ['POST'])
def client_close():
    userid = request.json['userid']
    port = active_userid_port.get(userid, None)
    if port:
        try:
            active_userid_port[userid] = None
            r = requests.post(f"http://localhost:{port}/interact",
                              json={'text': '[DONE]'})
        except requests.exceptions.ConnectionError:
            return {"status": f"close session with {userid}"}
    else:
        return {"status": f"no session with {userid}"}

if __name__ == '__main__':
    app.run(debug = True)