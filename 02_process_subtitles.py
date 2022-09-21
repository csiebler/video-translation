import os
import re
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()
output_raw_subtitles_path = os.getenv('OUTPUT_RAW_SUBTITLES_PATH')
output_processed_subtitles_path = os.getenv('OUTPUT_PROCESSED_SUBTITLES_PATH')

video_ids = os.listdir(output_raw_subtitles_path)
print(video_ids)

for video_id in video_ids:
    
    Path(f"{output_processed_subtitles_path}/{video_id}/").mkdir(parents=True, exist_ok=True)
    srt_files = os.listdir(f"{output_raw_subtitles_path}/{video_id}")
    print(srt_files)
       
    # Process all subtitles for the video
    for f in srt_files:
        with open(f"{output_raw_subtitles_path}/{video_id}/{f}", 'r', encoding='utf-8') as file:
            subtitles = file.read()
        subtitles += '\n\n'
    
        # loop through all numbers in srt file
        regex = re.compile('([0-9]+)\n([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})\n(.+?)\n{2}')
        r = regex.findall(subtitles)
        # print(r)
             
        subtitles = []
        for m in r:
            id = m[0]
            start = datetime.strptime(m[1],"%H:%M:%S,%f")
            end = datetime.strptime(m[2],"%H:%M:%S,%f")
            subtitle = {
                'start_ts': m[1],
                'end_ts': m[2],
                'start': start,
                'end': end,
                'duration': end-start,
                'text': m[3]
            }
            subtitles.append(subtitle)
            
        
        # merge subtitles if they are too close together
        merged_subtitles = []
        i = 0
        while i < len(subtitles):
            #print(f"{i}/{len(subtitles)}")
            
            current_subtitle = subtitles[i]
            
            j = i+1
            while j < len(subtitles):
                if (subtitles[j]['start'] - subtitles[j-1]['end']).total_seconds() < 0.11 and subtitles[j-1]['text'][-1] not in ['.', '!', '?']:
                    current_subtitle['end_ts'] = subtitles[j]['end_ts']
                    current_subtitle['duration'] += subtitles[j]['duration']
                    current_subtitle['text'] += ' ' + subtitles[j]['text']                 
                    print(f"Merged {j} to subtitle {i} to {current_subtitle['text']}")
                    j += 1
                else:
                    break;
                
            merged_subtitles.append(current_subtitle)
            i = j
                
        # write merged subtitles to file
        with open(f"{output_processed_subtitles_path}/{video_id}/{f}", 'w', encoding='utf-8') as file:
            for i in range(len(merged_subtitles)):
                file.write(f"{i+1}\n")
                file.write(f"{merged_subtitles[i]['start_ts']} --> {merged_subtitles[i]['end_ts']}\n")
                file.write(f"{merged_subtitles[i]['text']}\n")
                file.write("\n")