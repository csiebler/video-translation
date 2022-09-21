import os
import re
import yaml
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()
with open('settings.yml') as f:
    settings = yaml.safe_load(f)
    
output_processed_subtitles_path = os.getenv('OUTPUT_PROCESSED_SUBTITLES_PATH')
output_audio_snippet_path = os.getenv('OUTPUT_AUDIO_SNIPPETS_PATH')
speech_api_url = os.getenv('SPEECH_API_URL')
speech_api_key = os.getenv('SPEECH_API_KEY')

speakers = settings['voices']

headers = {
    "Ocp-Apim-Subscription-Key": speech_api_key,
    "X-Microsoft-OutputFormat": "riff-44100hz-16bit-mono-pcm",
    "Content-Type": "application/ssml+xml"
}


video_ids = os.listdir(output_processed_subtitles_path)

print(video_ids)

for video_id in video_ids:
    
    srt_files = os.listdir(f"{output_processed_subtitles_path}/{video_id}")
    srt_files.remove('original.srt')
    print(srt_files)
    
    for f in srt_files:
        with open(f"{output_processed_subtitles_path}/{video_id}/{f}", 'r', encoding='utf-8') as file:
            subtitles = file.read()
        subtitles += '\n\n'
        
        locale = f[:-4]
    
        Path(f"{output_audio_snippet_path}/{video_id}/{locale}").mkdir(parents=True, exist_ok=True) 

        print(f"Processing video {video_id} in locale {locale}")

        # loop through all numbers in srt file
        regex = re.compile('([0-9]+)\n([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})\n(.+?)\n{2}')
        r = regex.findall(subtitles)
        
        prompts = {}
        for m in r:
            id = m[0]
            start = datetime.strptime(m[1],"%H:%M:%S,%f")
            end = datetime.strptime(m[2],"%H:%M:%S,%f")
            prompt = {
                'start': start,
                'end': end,
                'duration': end-start,
                'text': m[3]
            }
            prompts[id] = prompt

        for id in prompts.keys():
            
            prompt = prompts[id]['text']
            speaker = speakers[locale]
            payload= f"""<speak version='1.0' xml:lang='en-US' xmlns:mstts="http://www.w3.org/2001/mstts" xmlns="http://www.w3.org/2001/10/synthesis"><voice xml:lang='en-US' xml:gender='Male'
                name='{speaker}'><mstts:silence type="tailing" value="100ms"/> 
                    {prompt}
            </voice></speak>
            """
            response = requests.post(speech_api_url, headers=headers, data=payload.encode('utf-8'))
            print(f"Status code: {response.status_code}")

            if response.status_code == 200:
                with open(f"{output_audio_snippet_path}/{video_id}/{locale}/{id}.wav", 'wb') as f:
                    f.write(response.content)
