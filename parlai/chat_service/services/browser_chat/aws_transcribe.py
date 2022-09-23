import time
import boto3
from pathlib import Path
from uuid import uuid4
import json
from urllib.request import urlopen

transcribe_client = boto3.client('transcribe', region_name = 'us-west-2')
def transcribe_file(file_uri):
    file_uri_p = Path(file_uri)
    job_name = f'job-{file_uri_p.stem}-{uuid4()}'
    transcribe_client.start_transcription_job(
        TranscriptionJobName = job_name,
        Media = {
            'MediaFileUri': file_uri
        },
        MediaFormat = file_uri_p.suffix[1:],
        LanguageCode = 'en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName = job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            if job_status == 'COMPLETED':
                url = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                return json.loads(urlopen(url).read())['results']['transcripts'][0]['transcript']
            elif job_status == 'FAILED':
                return 'FAILED'
        print(f'{max_tries}')
        time.sleep(5)
    return 'TIMEOUT'

#transcribe_file('s3://ai-user-voice/transcribe-sample.mp3')