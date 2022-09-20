from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
import requests
from dotenv import load_dotenv
import os 
import json

class VideoIndexerHelper:
    
    def __init__(self):
        load_dotenv()

        self.location = os.getenv('LOCATION')
        self.account_id = os.getenv('ACCOUNT_ID')
        self.account_name = os.getenv('ACCOUNT_NAME')
        self.resource_id = os.getenv('RESOURCE_ID')
        self.token = self.generate_token()

    def generate_token(self):
        credential = ChainedTokenCredential(ManagedIdentityCredential(), AzureCliCredential())
        access_token = credential.get_token("https://management.azure.com")

        headers = {
            "Authorization": f"Bearer {access_token.token}"
        }

        body = {
            "permissionType": "Contributor",
            "scope": "Account"
        }

        url = f"https://management.azure.com{self.resource_id}/generateAccessToken?api-version=2022-04-13-preview"
        response = requests.post(url, headers=headers, json=body)
        return response.json()['accessToken']

    def get_completed_video_ids(self):
        
        params = {
            'accessToken': self.token
        }
        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        response = requests.get(url, params=params)
        # print(f"Status code: {response.status_code}")
        # print(f"Response: {json.dumps(response.json(), indent=2)}")

        video_ids = []
        for video in response.json()['results']:
            if (video['state'] == 'Processed'):
                video_ids.append(video['id'])

        return video_ids
    
    
    def check_if_file_is_indexed(self, filename):
        params = {
            'accessToken': self.token
        }
        
        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        response = requests.get(url, params=params)
       
        found = False
        for video in response.json()['results']:
            if video['name'] == filename:
                found = True
                break
        return found

    def get_subtitle_for_video(self, video_id, locale):
        params = {
            'accessToken': self.token,
            'format': 'srt',
            'language': locale
        }
        
        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Captions"
        response = requests.get(url, params=params)
        return response.content

    def download_video(self, video_id, target_filename):
        params = {
            'accessToken': self.token
        }
        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/SourceFile/DownloadUrl"
        response = requests.get(url, params=params)
        download_url = response.content.replace(b'"', b'').decode('utf-8')
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(target_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    
    def upload_video(self, file_path, language_model_id=None):
        filename = os.path.basename(file_path)
        params = {
            'accessToken': self.token,
            'privacy': 'Private',
            'language': 'auto',
            'indexingPreset': 'AdvancedAudio',
            'name': filename
        }
        
        if language_model_id:
            params['linguisticModelId'] = language_model_id

        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        
        files = {'file': open(file_path, 'rb'), 'Content-Type':'multipart/form-data'}
        
        response = requests.post(url, params=params, files=files)
        print(response.status_code)
        print(response.text)
        