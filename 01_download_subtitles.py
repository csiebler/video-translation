import os
import yaml
from dotenv import load_dotenv
from pathlib import Path
from helper import VideoIndexerHelper

load_dotenv()
with open('settings.yml') as f:
    settings = yaml.safe_load(f)

output_raw_subtitles_path = os.getenv('OUTPUT_RAW_SUBTITLES_PATH')
output_video_path = os.getenv('OUTPUT_VIDEO_PATH')

locales = list(settings['voices'].keys())
print(f"Downloading subtitles for {locales}")

vi_client = VideoIndexerHelper()
video_ids = vi_client.get_completed_video_ids()
print(video_ids)
 
def save_subtitles_to_path(target_path, locale=None):
    srt = vi_client.get_subtitle_for_video(video_id, locale)
    with open(target_path, 'wb') as file:
        file.write(srt)

for video_id in video_ids:
    
    Path(f"{output_raw_subtitles_path}/{video_id}/").mkdir(parents=True, exist_ok=True) 
    
    # Download original subtitles
    target_path = f"{output_raw_subtitles_path}/{video_id}/original.srt"
    save_subtitles_to_path(target_path=target_path)
    
    # Download translated subtitles
    for locale in locales:
        target_path = f"{output_raw_subtitles_path}/{video_id}/{locale}.srt"
        save_subtitles_to_path(target_path=target_path, locale=locale)

    # Download video
    Path(f"{output_video_path}/{video_id}/").mkdir(parents=True, exist_ok=True)
    target_filename = f"{output_video_path}/{video_id}/source.mp4"
    vi_client.download_video(video_id, target_filename)
    print(f"Downloaded video for {video_id} to {target_filename}")
    
    # Extract audio from video to wav
    print(f"Extracting audio for {video_id}")
    output_audio = f"{output_video_path}/{video_id}/source.wav"
    # extract wav audio 16-bit stereo 44khz from mp4
    os.system(f"ffmpeg -i {target_filename} -y -vn -acodec pcm_s16le -ac 2 -ar 44100 {output_audio}")
    
