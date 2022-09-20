import os
import re
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from pydub import AudioSegment

load_dotenv()
output_processed_subtitles_path = os.getenv('OUTPUT_PROCESSED_SUBTITLES_PATH')
output_audio_snippet_path = os.getenv('OUTPUT_AUDIO_SNIPPETS_PATH')
output_audio_tracks_path = os.getenv('OUTPUT_AUDIO_TRACKS_PATH')

video_ids = os.listdir(output_processed_subtitles_path)
print(video_ids)

for video_id in video_ids:
    
    srt_files = os.listdir(f"{output_processed_subtitles_path}/{video_id}")
    print(srt_files)
    
    for f in srt_files:
        with open(f"{output_processed_subtitles_path}/{video_id}/{f}", 'r', encoding='utf-8') as file:
            subtitles = file.read()
        #subtitles += '\n\n'
        
        locale = f[:-4]
    
        Path(f"{output_audio_snippet_path}/{video_id}/{locale}").mkdir(parents=True, exist_ok=True) 

        print(f"Merging audio for video {video_id} in locale {locale}")

        # loop through all numbers in srt file
        regex = re.compile('([0-9]+)\n([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})\n(.+?)\n{2}')
        r = regex.findall(subtitles)
        # print(r)
        
        prompts = {}
        total_duration = 0
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
            total_duration = (end - datetime.strptime("00:00:00,000","%H:%M:%S,%f")).total_seconds()
        
        
        audio_track = AudioSegment.silent(duration=total_duration*1000)
        
        for id in prompts.keys():
            
            wave_file = f"{output_audio_snippet_path}/{video_id}/{locale}/{id}.wav"
            
            slice = AudioSegment.from_wav(wave_file)
            
            position = (prompts[id]['start'] - datetime.strptime("00:00:00,000","%H:%M:%S,%f")).total_seconds() * 1000
            print(position)
            audio_track = audio_track.overlay(slice, position=position)
        
        Path(f"{output_audio_tracks_path}/{video_id}").mkdir(parents=True, exist_ok=True) 
        audio_track.export(f"{output_audio_tracks_path}/{video_id}/{locale}.wav", format="wav")

