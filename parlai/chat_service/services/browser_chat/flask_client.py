from email import message
from flask import Flask, request
import requests
import time
from subprocess import Popen, PIPE
from parlai.chat_service.services.browser_chat.aws_transcribe import get_voice_to_text
from parlai.chat_service.services.browser_chat.aws_polly import get_text_to_voice
from parlai.chat_service.services.browser_chat.utils import get_chat_record, get_unused_port
import time
from parlai.chat_service.services.browser_chat.constants import MAX_CLIENT_IDLE_TIME, BOT_NAME, HISTORY_DIR, WEBSOCKET_PORT
from pathlib import Path
import websocket
import threading
import json
import atexit
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
# user_id: port, timestamp_latest_update
# userid: ws, message_available, new_message}
active_chat_session = {}

@scheduler.task('interval', id='delete_inactive_chat', seconds=30, misfire_grace_time=900)
def scheddelete_inactive_chatuled():
    ts = time.time()
    for user_id, v in active_chat_session.copy().items():
        ws, last_ts = v.values()        
        if (ts - last_ts) > MAX_CLIENT_IDLE_TIME:
            ws.close()
            del active_chat_session[user_id]
scheduler.start()


if not Path(HISTORY_DIR).exists():
    Path(HISTORY_DIR).mkdir(parents=True, exist_ok=True)


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

    if not active_chat_session.get(user_id, None):
        ws = websocket.WebSocketApp(
            "ws://localhost:{}/websocket".format(WEBSOCKET_PORT),
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.message_available = threading.Event()
        active_chat_session[user_id] = {
            'ws': ws,
            'timestamp': None
        }
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        time.sleep(0.1)
    else:
        ws = active_chat_session[user_id]['ws']

    data = {'userId': f'{user_id}',
            'text': f'{user_text}',
            'dateTime': f'{user_dt}'}
    json_data = json.dumps(data)
    ws.send(json_data)
    ws.message_available.wait()
    if ws.new_message == 'is_connected':
        ws.message_available.clear()
        ws.send(json_data)
        ws.message_available.wait()
    response = {}
    response['text'] = ai_text = ws.new_message
    ws.message_available.clear()
    response['userId'] = BOT_NAME
    response['dateTime'] = ai_dt = time.time()
    response['voice'] = ai_voice =get_text_to_voice(response['text'])

    with open(Path(HISTORY_DIR)/f'{user_id}.txt', 'a+') as f:
        # write user
        f.write(f'{user_dt}|{user_id}|{user_text}|{user_voice}\n')
        # write bot
        f.write(f'{ai_dt}|{BOT_NAME}|{ai_text}|{ai_voice}\n')
    active_chat_session[user_id]['timestamp'] = time.time()
    return response


@app.route('/client/retrievehistory', methods = ['GET'])
def retrievehistory():
    user_id = request.json['userId']
    data_number = request.json.get('dataNumber', 0)
    chat_record = get_chat_record(user_id, data_number)
    return {"userId": user_id,
            "chatRecord": chat_record}


def on_message(ws, message):
    """
    Prints the incoming message from the server.

    :param ws: a WebSocketApp
    :param message: json with 'text' field to be printed
    """
    incoming_message = json.loads(message)
    ws.new_message = incoming_message['text']
    ws.message_available.set()


def on_error(ws, error):
    """
    Prints an error, if occurs.

    :param ws: WebSocketApp
    :param error: An error
    """
    print(error)


def on_close(ws):
    """
    Cleanup before closing connection.

    :param ws: WebSocketApp
    """
    # Reset color formatting if necessary
    print("Connection closed")


if __name__ == '__main__':
    app.run(debug = True)
