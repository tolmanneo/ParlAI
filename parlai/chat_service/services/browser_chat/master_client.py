from flask import Flask, request
import requests
import time
from subprocess import Popen, PIPE
from aws_transcribe import get_voice_to_text
from aws_polly import get_text_to_voice
from utils import get_chat_record, get_unused_port
import time
from constants import MAX_CLIENT_IDLE_TIME, BOT_NAME, HISTORY_DIR, NLP_PORT
from pathlib import Path

app = Flask(__name__)

# user_id: port, timestamp_latest_update
active_userid_port = {}
print(Path(HISTORY_DIR).exists())
if not Path(HISTORY_DIR).exists():
    Path(HISTORY_DIR).mkdir(parents=True, exist_ok=True)

# run a cron job every xxx min to clear up idle users
@app.cli.command()
def scheduled():
    ts = time()
    for _, port_ts in active_userid_port.items():
        port, ts_user_id = port_ts.values()
        if (ts - ts_user_id) > MAX_CLIENT_IDLE_TIME:
            request.post(f"http://127.0.0.1:{port}/interact",
                         json={'text': '[DONE]'})


@app.route('/client/talktoai', methods = ['POST'])
def talktoai():
    # form request
    user_id = request.json['userId']
    user_dt = request.json['dateTime']
    if 'voice' in request.json:
        user_voice = request.json['voice']
        user_text = get_voice_to_text(user_voice)
    else:
        user_voice = ''
        user_text = request.json['text']

    if not active_userid_port.get(user_id, None):
        port = get_unused_port()
        Popen(['python', 'client.py', '--port', f'{NLP_PORT}', '--serving-port', str(port)])
        active_userid_port[user_id] = port
        print('sleep 2 sec')
        time.sleep(2)
    else:
        port = active_userid_port[user_id]

    print(f'come here, port created is: {port}')
    r = requests.post(f"http://127.0.0.1:{port}/interact",
                        json={'userId': f'{user_id}',
                              'text': f'{user_text}',
                              'dateTime': f'{user_dt}'},
                        timeout=10000000)

    if r.json()['text'] == f'is_connected':
        r = requests.post(f"http://127.0.0.1:{port}/interact",
                            json={'userId': f'{user_id}',
                                  'text': f'{user_text}',
                                  'dateTime': f'{user_dt}'},
                        timeout=10000000)

    result = r.json()
    ai_text = result['text']
    result['userId'] = BOT_NAME
    ai_dt = result['dateTime'] = time.time()
    ai_voice = result['voice'] = get_text_to_voice(result['text'])

    with open(Path(HISTORY_DIR)/f'{user_id}.txt', 'a+') as f:
        # write user
        f.write(f'{user_dt}|{user_id}|{user_text}|{user_voice}\n')
        # write bot
        f.write(f'{ai_dt}|{BOT_NAME}|{ai_text}|{ai_voice}\n')

    return result


@app.route('/client/retrievehistory', methods = ['GET'])
def retrievehistory():
    user_id = request.json['userId']
    data_number = request.json.get('dataNumber', 0)
    chat_record = get_chat_record(user_id, data_number)
    return {"userId": user_id,
            "chatRecord": chat_record}


if __name__ == '__main__':
    app.run(debug = True)
