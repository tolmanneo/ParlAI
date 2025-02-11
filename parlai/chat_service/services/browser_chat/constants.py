import os

MAX_CLIENT_IDLE_TIME = 30 # 1 min
MAX_CHAT_HISTORY = 20
BOT_NAME = 'AI'
HISTORY_DIR = f"{os.getenv('HOME')}/chat_history"
SPEAKER_SELF = 'RoboChoom'
SPEAKER_OTHER = 'Human'
WEBSOCKET_PORT = 10002
AWS_S3_VOICE_INPUT = 'ai-voice-input'
AWS_S3_VOICE_OUTPUT = 'ai-voice-output'
AWS_VOICE_NAME = 'Lucia'
STORY_CONTEXT = f'{os.path.dirname(__file__)}/text.txt'
LOCAL_VOICE_OUTPUT = f"{os.getenv('HOME')}/user_voice"
NLP_SERVER = 'http://127.0.0.1:30001'

