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
 

for video_id in video_ids:
    
    Path(f"{output_raw_subtitles_path}/{video_id}/").mkdir(parents=True, exist_ok=True) 
    
    for locale in locales:
        srt = vi_client.get_subtitle_for_video(video_id, locale)
        target_srt_path = f"{output_raw_subtitles_path}/{video_id}/{locale}.srt"
        with open(target_srt_path, 'wb') as file:
            file.write(srt)
        print(f"Downloaded subtitles for {video_id} in {locale}")

    Path(f"{output_video_path}/{video_id}/").mkdir(parents=True, exist_ok=True)
    target_filename = f"{output_video_path}/{video_id}/source.mp4"
    vi_client.download_video(video_id, target_filename)
    print(f"Downloaded video for {video_id} to {target_filename}")

