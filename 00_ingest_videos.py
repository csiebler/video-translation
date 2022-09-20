import os
import yaml
from dotenv import load_dotenv
from helper import VideoIndexerHelper

load_dotenv()
input_video_path = os.getenv('INPUT_VIDEO_PATH')

with open('settings.yml') as f:
    settings = yaml.safe_load(f)

videos = os.listdir(input_video_path)
print(videos)

vi_client = VideoIndexerHelper()

for video in videos:
    if not vi_client.check_if_file_is_indexed(video):
        print(f"Uploading {video}")
        vi_client.upload_video(f"{input_video_path}/{video}")
    else:
        print(f"Video {video} has already been indexed")
