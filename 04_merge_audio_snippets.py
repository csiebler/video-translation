import os
import re
import yaml
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from pydub import AudioSegment

load_dotenv()
with open('settings.yml') as f:
    settings = yaml.safe_load(f)
    
output_processed_subtitles_path = os.getenv('OUTPUT_PROCESSED_SUBTITLES_PATH')
output_audio_snippet_path = os.getenv('OUTPUT_AUDIO_SNIPPETS_PATH')
output_audio_tracks_path = os.getenv('OUTPUT_AUDIO_TRACKS_PATH')
original_audio_path = os.getenv('OUTPUT_VIDEO_PATH')
overdub_original_audio = settings['overdub_original_audio']

video_ids = os.listdir(output_processed_subtitles_path)
print(video_ids)


def read_subtitles(subtitle_path):
    with open(subtitle_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    regex = re.compile('([0-9]+)\n([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})\n(.+?)\n{2}')
    lines = regex.findall(srt_content)
    subtitles = []
    total_duration = 0
    for sub in lines:
        start = int((datetime.strptime(sub[1],"%H:%M:%S,%f") - datetime.strptime("00:00:00,000","%H:%M:%S,%f")).total_seconds() * 1000)
        end = int((datetime.strptime(sub[2],"%H:%M:%S,%f") - datetime.strptime("00:00:00,000","%H:%M:%S,%f")).total_seconds() * 1000)
        processed_subtitle = {
            'id': sub[0],
            'start': start,
            'end': end,
            'duration': end-start,
            'text': sub[3]
        }
        subtitles.append(processed_subtitle)
        total_duration = end
    return subtitles, total_duration

for video_id in video_ids:
    
    srt_files = os.listdir(f"{output_processed_subtitles_path}/{video_id}")
    srt_files.remove('original.srt')
    print(srt_files)
    
    original_subtitles, original_duration = read_subtitles(subtitle_path=f"{output_processed_subtitles_path}/{video_id}/original.srt")
    
    for f in srt_files:
        locale = f[:-4]
        subtitle_path = f"{output_processed_subtitles_path}/{video_id}/{f}"
        subtitles, total_duration = read_subtitles(subtitle_path=subtitle_path)

        if overdub_original_audio:
            print(f"Overdubbing original audio for video {video_id} in locale {locale}")
            audio_track = AudioSegment.from_file(f"{original_audio_path}/{video_id}/source.wav", format="wav")
            for s in original_subtitles:
                silence = AudioSegment.silent(duration=s['duration'])
                audio_track = audio_track.overlay(silence, position=s['start'], gain_during_overlay=-50)
        else:
            print(f"Creating new empty audio track for video {video_id} in locale {locale}")
            audio_track = AudioSegment.silent(duration=total_duration)
            
        for subtitle in subtitles:
            wave_file = f"{output_audio_snippet_path}/{video_id}/{locale}/{subtitle['id']}.wav"
            slice = AudioSegment.from_wav(wave_file)
            audio_track = audio_track.overlay(slice, position=subtitle['start'])
        
        Path(f"{output_audio_tracks_path}/{video_id}").mkdir(parents=True, exist_ok=True) 
        audio_track.export(f"{output_audio_tracks_path}/{video_id}/{locale}.wav", format="wav")

