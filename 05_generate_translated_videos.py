import os
from dotenv import load_dotenv

load_dotenv()
output_audio_tracks_path = os.getenv('OUTPUT_AUDIO_TRACKS_PATH')
output_video_path = os.getenv('OUTPUT_VIDEO_PATH')
video_ids = os.listdir(output_video_path)

for video_id in video_ids:
    
    audio_tracks = os.listdir(f"{output_audio_tracks_path}/{video_id}/")
    source_video_file = f"{output_video_path}/{video_id}/source.mp4"
    
    for audio_track in audio_tracks:
        
        source_audio_file = f"{output_audio_tracks_path}/{video_id}/{audio_track}"
        target_video_file = f"{output_video_path}/{video_id}/{audio_track[:-4]}.mp4"
        print(f"Multiplexing {source_audio_file} to video {source_video_file} into new file {target_video_file}")
        os.system(f"ffmpeg -y -i {source_video_file} -i {source_audio_file} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {target_video_file}")