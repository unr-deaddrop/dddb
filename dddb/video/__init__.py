import unittest
import os
import sys
from timeit import default_timer as timer
from math import ceil
import numpy
import cv2
import tempfile

class dddbEncodeVideo:
    def __init__(self, data:bytes, px=1920, py=1280, n=10):
        assert isinstance(data, bytes)
        start=timer()
        self.tempfile = tempfile.NamedTemporaryFile(suffix=".mp4", mode="w+b", delete=False)
        self.tempfile.close()
        self.data = data + b'\x01';
        by=int(py/n)
        bx=int(px/n)
        bpf = int(by*bx)
        data = numpy.unpackbits(
                numpy.frombuffer(self.data, dtype=numpy.uint8)) * 0xFF
        data[-1] = 0x77;
        data[-2] = 0x77;
        data[-3] = 0x77;
        data[-4] = 0x77;
        data[-5] = 0x77;
        data[-6] = 0x77;
        data[-7] = 0x77;
        data[-8] = 0x77;
        fct = int(ceil(len(data)/bpf)+1)
        data.resize(by*bx*fct)
        data = data.reshape(fct,by,bx,1)
        data = data.repeat(n, axis=1).repeat(n, axis=2).repeat(3, axis=3)
        
        if sys.platform == "win32":
            # On Windows, use the avc1 codec. This was the codec used when
            # fourcc_codec == -1, and was the only one we found to work on
            # our installations.
            fourcc_codec = 0x31637661
            # fourcc_codec = cv2.VideoWriter_fourcc(*'avc1')
        else:
            # By default, use the mp4v codec. This is expected to work in Docker
            # environments.
            fourcc_codec = cv2.VideoWriter_fourcc(*'mp4v')
        
        video = cv2.VideoWriter(self.getFile().name, fourcc_codec, 5, (px, py))
        for i in data:
            video.write(i)
        video.release()
        self.time = timer()-start

    def getFile(self):
        return self.tempfile

    def getBytes(self):
        with open(self.getFile().name, "rb") as f:
            return f.read()

    def getBPS(self):
        return len(self.data) / self.time

class dddbDecodeVideo:
    def __init__(self, data:bytes, px=1920, py=1280, n=10):
        assert isinstance(data, bytes)
        start=timer()
        self.tempfile = tempfile.NamedTemporaryFile(suffix=".mp4", mode="w+b", delete=False)
        self.tempfile.close()
        by=int(py/n)
        bx=int(px/n)
        bpf=int(by*bx)
        with open(self.getFile().name, "w+b") as f:
            f.write(data)
        video = cv2.VideoCapture(self.getFile().name)
        data = []
        ret = True
        while(ret):
            ret, frame = video.read()
            if ret:
                data.append(frame)
        data = numpy.stack(data, axis=0)
        video.release()
        data = data[::1,::n,::n,::3]
        data = data.reshape(data.size)
        data = numpy.round(data / 0xff, 0)
        self.data = numpy.packbits(data.astype(numpy.uint8)).tobytes().rstrip(b'\x00')
        self.time = timer()-start

    def getFile(self):
        return self.tempfile

    def getBytes(self):
        return self.data

    def getBPS(self):
        return len(self.data) / self.time




class TestDddbVideo(unittest.TestCase):
    def test_encode(self):

        dddbVideoEncodeObj = dddbEncodeVideo(b"echo 'hello'")
        print("Successfully encoded video")

    def test_decode(self):
        with open(os.path.dirname(os.path.realpath(__file__))+"/bee-movie.txt","rb") as f:
            string = f.read()
        dddbVideoEncodeObj = dddbEncodeVideo(string)
        dddbVideoDecodeObj = dddbDecodeVideo(dddbVideoEncodeObj.getBytes())
        assert dddbVideoDecodeObj.getBytes() == string
        print("Successfully encode and decoded video")
        print(str(dddbVideoDecodeObj.getBPS())+" Bytes/Second decode")
        print(str(dddbVideoEncodeObj.getBPS())+" Bytes/Second encode")

if __name__ == "__main__":
    unittest.main()
