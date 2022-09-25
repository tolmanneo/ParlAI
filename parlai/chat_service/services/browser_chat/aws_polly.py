from contextlib import closing
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4
import os

polly_client = boto3.client('polly', region_name = 'us-west-2')
s3_client = boto3.client('s3', region_name = 'us-west-2')
bucket = 'ai-voice-output'
dir_path =f"{os.getenv('HOME')}/user_voice"
if not os.path.exists(dir_path):
    os.mkdir(dir_path)

def get_text_to_voice(text):
    try:
        # Request speech synthesis
        response = polly_client.synthesize_speech(Text=text, OutputFormat="mp3",
                                                  Engine='neural',
                                                  VoiceId='Brian')
        code = str(uuid4())
        file_path = f'{dir_path}/{code}.mp3'
        with closing(response['AudioStream']) as stream:
            with open(file_path, 'wb') as file:
                file.write(stream.read())
        
        response = s3_client.upload_file(file_path, bucket, f'{code}.mp3')
        return f"s3://{bucket}/{code}.mp3"
    except (BotoCoreError, ClientError) as error:
        return f'FAILED'

#get_voice('rock and roll')
# for voice in voices:
#     a = get_voice('This is a text for text to speech. A little hard a little soft but always on point',
#                 voice)
#     if a != f'FAILED {voice}':
#         print(f'{voice} done')
#         with closing(a['AudioStream']) as stream:
#             with open(f'/home/moe/polly_voice/{voice}.mp3', 'wb') as file:
#                 file.write(stream.read())
#     else:
#         print(a)