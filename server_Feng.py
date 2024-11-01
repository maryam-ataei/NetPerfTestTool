#!/usr/bin/python3

 

 

from http.server import HTTPServer, BaseHTTPRequestHandler

from random import randbytes

import socketserver

import time

 

port = 5201

 

 

 

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):

        self.protocol_version = "HTTP/1.1"

        super().__init__(request, client_address, server)

 

    def get_random_data(l: int):

        return randbytes(l)

 

    def do_GET(self):

        duration = 5                           #default video chunk duration 5

        encoding_rate = 1 * 1024 * 1024        #default encoding rate 1Mbps

 

        print(self.headers)

 

        if "Encoding-Rate-kbps" in self.headers:

            encoding_rate = int(self.headers["Encoding-Rate-kbps"]) * 1024

 

        if "Start-Time" in self.headers and "Stop-Time" in self.headers:

            start_tm = float(self.headers["Start-Time"])

            stop_tm = float(self.headers["Stop-Time"])

            duration = max(1, stop_tm - start_tm)

 

        size = int((duration * encoding_rate)) // 8

 

        self.send_response(200)

        self.send_header("Content-type", "application/stream")

        self.send_header("Connection", "keep-alive")

        #self.send_header("keep-alive", "timeout=10, max=30")

        self.send_header("Content-Length", size)

        self.end_headers()

        self.wfile.write(randbytes(size))

 

 

with socketserver.TCPServer(('', port), SimpleHTTPRequestHandler) as httpd:

    print("serving at port", port)

    httpd.serve_forever()