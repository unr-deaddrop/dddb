import requests
import unittest
import sys
import path
import os
sys.path.append(path.Path(__file__).abspath().parent.parent.parent.parent)
import dddb.video
class dddbFakeVideo:
    def __init__(self, ipaddr):
        self.ipaddr = ipaddr
    def post(self, data:bytes):
        requests.post("http://"+self.ipaddr, data=data, headers={"Content-Length": str(len(data))})
    def get(self):
        return requests.get("http://"+self.ipaddr).content

class TestDddbFakeVideo(unittest.TestCase):
    def test_upload(self):
        dddbFakeVideoObj = dddbFakeVideo("172.17.0.2")
        dddbVideoEncodeObj = dddb.video.dddbEncodeVideo(b"echo 'hello'")
        dddbFakeVideoObj.post(dddbVideoEncodeObj.getBytes())
    def test_download(self):
        with open(os.path.dirname(os.path.realpath(__file__))+"/../bee-movie.txt","rb") as f:
            string = f.read()
        dddbFakeVideoObj = dddbFakeVideo("172.17.0.2")
        dddbVideoEncodeObj = dddb.video.dddbEncodeVideo(string)
        dddbFakeVideoObj.post(dddbVideoEncodeObj.getBytes())
        dddbVideoDecodeObj = dddb.video.dddbDecodeVideo(dddbFakeVideoObj.get())
        assert dddbVideoDecodeObj.getBytes() == string

if __name__ == "__main__":
    unittest.main()
