import requests
import os
import sys
import time
import json
import moviepy.editor


import moviepy.editor
from tkinter.filedialog import *
video = askopenfilename()
name = video.split('/')[-1].split('.')[0]
video = moviepy.editor.VideoFileClip(video)
audio = video.audio
audio.write_audiofile(f"{name}.mp3")
print("Completed!")

#---------#

filename = (f'/Users/omjodhpurkar/Documents/All/projects/Song summarise/{name}.mp3')
api_key = '77bdb4832f5242668543d5dbe29521f2'
upload_endpoint = 'https://api.assemblyai.com/v2/upload'

def read_file(filename, chunk_size=5242880):
    with open(filename, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


headers = {'authorization': api_key,
           'content-type': 'application/json'}
response = requests.post(upload_endpoint,
                         headers=headers,
                         data=read_file(filename))

audio_url = response.json()['upload_url']
#---------#
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

response = requests.post(transcript_endpoint,
                         headers=headers,
                         json={
                             "audio_url": audio_url,
                             "auto_chapters": True
                         })
transcript_id = response.json()['id']
#---------#
polling_endpoint =  os.path.join(transcript_endpoint, transcript_id)

status = ''
while status != 'completed':
    response_result = requests.get(
        polling_endpoint,
        headers=headers
    )
    status = response_result.json()['status']
    print(f'Status: {status}')

    if status == 'error':
        sys.exit('Audio file failed to process.')
    elif status != 'completed':
        time.sleep(10)


if status == 'completed':
    filename = name + '.txt'
    with open(filename, 'w') as f:
        f.write(response_result.json()['text'])

    filename = transcript_id + '_chapters.json'
    with open(filename, 'w') as f:
        chapters = response_result.json()['chapters']
        json.dump(chapters, f, indent=4)

    print('Transcript Saved')