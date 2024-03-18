import unittest
import os
from timeit import default_timer as timer
from math import ceil
import numpy
import cv2
import tempfile

class dddbEncodeVideo:
    def __init__(self, data:bytes, px=1920, py=1080, n=5):
        assert isinstance(data, bytes)
        start=timer()
        self.tempfile = tempfile.NamedTemporaryFile(suffix=".avi", mode="w+b")
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
        video = cv2.VideoWriter(self.getFile(), cv2.VideoWriter_fourcc(*"MJPG"), 30, (px, py))
        self.tempfile.flush()
        for i in data:
            video.write(i)
        video.release()
        self.time = timer()-start

    def getFile(self):
        return self.tempfile.name

    def getBytes(self):
        with open(self.getFile(), "rb") as f:
            data = f.read()
            f.close()
            return data

    def getBPS(self):
        return len(self.data) / self.time

class dddbDecodeVideo:
    def __init__(self, data:bytes, px=1920, py=1080, n=5):
        assert isinstance(data, bytes)
        start=timer()
        self.tempfile = tempfile.NamedTemporaryFile(suffix=".avi", mode="w+b")
        by=int(py/n)
        bx=int(px/n)
        bpf=int(by*bx)
        with open(self.getFile(),"wb") as f:
            f.write(data)
        video = cv2.VideoCapture(self.getFile())
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
        end = numpy.where(numpy.logical_and(data > 0x20, data < 0xA0))[0][0]
        data = data[:end]
        data = numpy.round(data / 0xff, 0)
        self.data = numpy.packbits(data.astype(numpy.uint8)).tobytes()
        self.time = timer()-start

    def getFile(self):
        return self.tempfile.name

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
