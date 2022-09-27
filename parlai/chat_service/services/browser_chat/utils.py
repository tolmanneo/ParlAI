from pathlib import Path
from parlai.chat_service.services.browser_chat.constants import HISTORY_DIR
import socket


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


def get_chat_record(user_id, data_number):
    chat_record = []
    if data_number == 0:
        return chat_record
    else:
        with open(Path(HISTORY_DIR)/f'{user_id}.txt', 'r') as f:
            chat_history = f.readlines()
            chat_len = min(len(chat_history), data_number)
            for line in chat_history[-chat_len:]:
                dt, agent, text, voice = line.strip().split('|')
                chat_line = {
                    'dateTime': float(dt),
                    'from': agent}
                if voice:
                    chat_line['voice'] = voice
                else:
                    chat_line['text'] = text
                chat_record.append(chat_line)
        return chat_record