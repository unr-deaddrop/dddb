import requests
import unittest
import sys
from converter import Converter
import path
import os
import json
from time import time
sys.path.append(path.Path(__file__).abspath().parent.parent.parent.parent)
import dddb.video
import peertube
from collections import ChainMap
import tempfile
class dddbPeerTube:
    def __init__(self, host, username, password):
        self.host = host
        self.info = {
            'username': username,
            'password': password,
            'response_type': 'code',
            'grant_type': 'password'
        }
        self.user_token = None
        self.authenticate()

    def authenticate(self):
        if self.is_authenticated():
            return True
        client = requests.get(self.host+"/api/v1/oauth-clients/local")
        if client.status_code != 200:
            self.user_token = None
            return False
        self.client = client.json()
        user_token = requests.post(self.host+"/api/v1/users/token", data=ChainMap(self.client, self.info))
        if user_token.status_code != 200:
            self.user_token = None
            return False
        self.user_token = user_token.json()
        self.token_expires = time() + self.user_token['expires_in']
        self.configuration = peertube.Configuration(
                host = self.host+"/api/v1"
        )
        self.configuration.access_token = self.user_token['access_token']
        return True

    def post(self, data:bytes, dest, src, channel_id = 1):
        self.authenticate()
        avitf = tempfile.NamedTemporaryFile(suffix=".avi", mode="w+b")
        with open(avitf.name, "w+b") as f:
            f.write(data)
        mp4tf = tempfile.NamedTemporaryFile(suffix=".mp4")
        c = Converter()
        info = c.probe(avitf.name)
        conv = c.convert(avitf.name, mp4tf.name,
                         {
                            'format': 'mp4',
                            'video': {
                                'codec': 'hevc',
                                'width': info.video.video_width,
                                'heigth': info.video.video_height,
                                'fps': info.video.video_fps
                            }
                         })
        for timecode in conv:
            print("Convert to mp4")
        with peertube.ApiClient(self.configuration) as api_client:
            api_instance = peertube.VideoApi(api_client)
            try: 
                api_response = api_instance.videos_upload_post(mp4tf.name, channel_id, json.dumps({"timestamp": time(), "dest": dest, "src": src}), privacy=1)
            except peertube.ApiException as e:
                print("failed to post to peertube")
                print(e)
                return False
        return True

    def get(self, dest, channel_id=1, delete=True):
        self.authenticate()
        ret = []
        with peertube.ApiClient(self.configuration) as api_client:
            api_instance = peertube.VideoApi(api_client)
            try: 
                videos_data = api_instance.videos_get().to_dict()
                for video_data in videos_data['data']:
                    if video_data['channel']['id'] == channel_id:
                        meta = json.loads(video_data['name'])
                        if meta['dest'] == dest:
                            try:
                                video = api_instance.videos_id_get(video_data['id'])
                                video=video.to_dict()
                                if len(video['files']):
                                    url = video['files'][0]['file_download_url'].replace("http://localhost:9000", self.host)
                                else:
                                    continue
                                ret.append(meta)
                                filedownload = requests.get(url)
                                avitf = tempfile.NamedTemporaryFile(suffix=".avi")
                                mp4tf = tempfile.NamedTemporaryFile(suffix=".mp4")
                                with open(mp4tf.name, "w+b") as f:
                                    f.write(filedownload.content)
                                c = Converter()
                                info = c.probe(mp4tf.name)
                                conv = c.convert(mp4tf.name, avitf.name,
                                                 {
                                                    'format': 'avi',
                                                    'video': {
                                                        'codec': 'copy',
                                                        'width': info.video.video_width,
                                                        'heigth': info.video.video_height,
                                                        'fps': info.video.video_fps
                                                    }
                                                 })
                                for timecode in conv:
                                    print("Converting to avi")
                                with open(avitf.name, "rb") as f:
                                    ret[-1]['data'] = f.read()
                                if delete:
                                    try:
                                        api_instance.videos_id_delete(video_data['id'])
                                    except peertube.ApiException as e:
                                        print("failed to delete video from peertube")
                                        print(e)
                            except peertube.ApiException as e:
                                print("failed to get videos from peertube")
                                print(e)
                                return ret

            except peertube.ApiException as e:
                print("failed to get videos from peertube")
                print(e)
                return ret
        return ret

    def is_authenticated(self):
        return self.user_token and time() < self.token_expires

class TestDddbPeerTube(unittest.TestCase):
    def test_connect(self):
        peerTubeObj = dddbPeerTube("http://192.168.1.166:9000", "root", "deaddrop")
        assert peerTubeObj.is_authenticated()

    def test_post(self):
        with open(os.path.dirname(os.path.realpath(__file__))+"/../bee-movie.txt","rb") as f:
            string = f.read()
        dddbPeerTubeObj = dddbPeerTube("http://192.168.1.166:9000", "root", "deaddrop")
        dddbPeerTubeObj.authenticate()
        dddbVideoEncodeObj = dddb.video.dddbEncodeVideo(string)
        assert dddbPeerTubeObj.post(dddbVideoEncodeObj.getBytes(), dest="test2", src="test1")
        response = dddbPeerTubeObj.get(dest="test2", delete=False)
        dddbVideoDecodeObj = dddb.video.dddbDecodeVideo(response[0]['data'])
        print("len out:",len(dddbVideoDecodeObj.getBytes()))
        print("len in:",len(string))

if __name__ == "__main__":
    unittest.main()
