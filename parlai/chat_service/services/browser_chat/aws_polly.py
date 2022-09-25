from contextlib import closing
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4
import os
from constants import AWS_S3_VOICE_OUTPUT, LOCAL_VOICE_OUTPUT, AWS_VOICE_NAME

polly_client = boto3.client('polly', region_name = 'us-west-2')
s3_client = boto3.client('s3', region_name = 'us-west-2')
bucket = AWS_S3_VOICE_OUTPUT
dir_path = LOCAL_VOICE_OUTPUT

if not os.path.exists(dir_path):
    os.mkdir(dir_path)

def get_text_to_voice(text):
    try:
        # Request speech synthesis
        response = polly_client.synthesize_speech(Text=text, OutputFormat="mp3",
                                                  Engine='neural',
                                                  VoiceId=AWS_VOICE_NAME)
        code = str(uuid4())
        file_path = f'{dir_path}/{code}.mp3'
        with closing(response['AudioStream']) as stream:
            with open(file_path, 'wb') as file:
                file.write(stream.read())
        
        response = s3_client.upload_file(file_path, bucket, f'{code}.mp3')
        return f"s3://{bucket}/{code}.mp3"
    except (BotoCoreError, ClientError) as error:
        return f'FAILED'
