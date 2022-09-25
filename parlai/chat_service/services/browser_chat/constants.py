import os

MAX_CLIENT_IDLE_TIME = 60 # 1 min
MAX_CHAT_HISTORY = 20
BOT_NAME = 'AI'
HISTORY_DIR = f"{os.getenv('HOME')}/chat_history"
SPEAKER_SELF = 'RoboChoom'
SPEAKER_OTHER = 'Human'
NLP_PORT = 10002
AWS_S3_VOICE_INPUT = 'ai-voice-input'
AWS_S3_VOICE_OUTPUT = 'ai-voice-output'
STORY_CONTEXT = f'{os.path.dirname(__file__)}/text.txt'
LOCAL_VOICE_OUTPUT = f"{os.getenv('HOME')}/user_voice"
NLP_SERVER = 'http://localhost:30001'