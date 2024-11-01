#!/bin/python3

 

import http.client

import time

 

 

path = "/dummy_video"

http_cmd = "GET"

 

video_chunk_duration = 4

 

video_segment_encodings = [ {"Encoding-Rate-kbps" : 5000,

                            "Start-Time" : 0,

                            "Stop-Time"  : 12},

                           {"Encoding-Rate-kbps" : 10000,

                            "Start-Time" : 12,

                            "Stop-Time"  : 24}

                          ]

 

host = "172.31.42.18"

port = 5201

conn = http.client.HTTPConnection(host, port)

conn.connect()

 

cnt = 0

begin_time = time.time()

for seg in video_segment_encodings :

    now = seg["Start-Time"]

    headers = {}

    while now < seg["Stop-Time"]:

        headers["Start-Time"] = now

        headers["Stop-Time"] = min(now + video_chunk_duration, seg["Stop-Time"])

        now = headers["Stop-Time"]

        headers["Encoding-Rate-kbps"] = encoding_rate = seg["Encoding-Rate-kbps"]

        cnt += 1

 

        startTime = time.time()

        conn.request(http_cmd, path, headers = headers)

        res = conn.getresponse()

        data = res.read()

        endTime = time.time()

        elapsedTime = endTime - startTime

        wall_clock_time = time.time() - begin_time

        print(f"Time: {wall_clock_time:.6f}, received: #{cnt} chunk, {len(data)} bytes, encoding-rate-kbps: " +

              f"{encoding_rate}, in {elapsedTime:.6f} sec, thrput-mbps: {len(data) * 8 / (1024 * 1024 * elapsedTime):.6}.")

        time.sleep(max(1, now - headers["Start-Time"] - elapsedTime))

    #next video segment