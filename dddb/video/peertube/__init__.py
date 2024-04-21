import requests
import unittest
import sys
import path
import os
from time import time
sys.path.append(path.Path(__file__).abspath().parent.parent.parent.parent)
import dddb.video
import peertube
from collections import ChainMap
class dddbPeerTube:
    def __init__(self, host, username, password):
        self.host = host
        self.info = {
            'username': username,
            'password': password,
            'response_type': 'code',
            'grant_type': 'password'
        }
        self.authenticate()

    def authenticate(self):
        client = requests.get(self.host+"/api/v1/oauth-clients/local")
        if client.status_code != 200:
            self.user_token = {}
            return False
        self.client = client.json()
        user_token = requests.post(self.host+"/api/v1/users/token", data=ChainMap(self.client, self.info))
        if user_token.status_code != 200:
            self.user_token = {}
            return False
        self.user_token = user_token.json()
        self.token_expires = time() + self.user_token['expires_in']
        self.configuration = peertube.Configuration(
                host = self.host+"/api/v1"
        )
        self.configuration.access_token = self.user_token['access_token']

    def post(self, path, name, channel_id = 1):
        with peertube.ApiClient(self.configuration) as api_client:
            api_instance = peertube.VideoApi(api_client)
            try: 
                api_response = api_instance.videos_upload_post(path, channel_id, name)
                print(api_response)
            except peertube.ApiException as e:
                print("failed to post to peertube")
                print(e)
                return False
        return True

    def is_authenticated(self):
        return self.user_token and time() < self.token_expires

class TestDddbPeerTube(unittest.TestCase):
    def test_connect(self):
        peerTubeObj = dddbPeerTube("http://192.168.1.166:3000", "root", "deaddrop")
        peerTubeObj.authenticate()
        assert peerTubeObj.is_authenticated()

    def test_post(self):
        dddbPeerTubeObj = dddbPeerTube("http://192.168.1.166:3000", "root", "deaddrop")
        dddbVideoEncodeObj = dddb.video.dddbEncodeVideo(b"echo 'hello'")
        assert dddbPeerTubeObj.post(dddbVideoEncodeObj.getFile(), "hello")

if __name__ == "__main__":
    unittest.main()
