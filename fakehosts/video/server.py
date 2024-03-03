#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import tempfile
import socket
hostName = "0.0.0.0"
serverPort = 80
class Handler(BaseHTTPRequestHandler):
    tempfile = tempfile.NamedTemporaryFile(suffix=".avi", mode="w+b")
    print(socket.gethostbyname(socket.gethostname())+":"+str(serverPort))
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "video/x-msvideo")
            self.end_headers()
            with open(self.tempfile.name, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
        return
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello")
        content_len = int(self.headers.get('Content-Length'))
        data = self.rfile.read(content_len)
        with open(self.tempfile.name, "wb") as f:
            f.write(data)
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """http threaded server"""

if __name__ == "__main__":
    webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print('Server stopped.')
