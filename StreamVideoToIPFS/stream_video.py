#! /usr/bin/python

import cv2
import subprocess
import time
import ipfshttpclient
import asyncio
from threading import Thread
import signal
import sys

# Normally you would open the video directly from source, but
# I'm using WSL and it's not possible to get a direct video feed.

# Open RTMP stream
cap = cv2.VideoCapture("rtmp://localhost/live/input")
# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Get input video dimensions
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set output video dimensions
RESIZE_FACTOR = 4
rewidth = int(width / RESIZE_FACTOR)
reheight = int(height / RESIZE_FACTOR)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
CHUNK_LENGTH = 15  # seconds

# Output to RTMP stream
# FOR DEBUG
# command = ['ffmpeg',
#            '-y',
#            '-f', 'rawvideo',
#            '-vcodec', 'rawvideo',
#            '-pix_fmt', 'bgr24',
#            '-s', "{}x{}".format(rewidth, reheight),
#            '-r', str(fps),
#            '-i', '-',
#            '-c:v', 'libx264',
#            '-pix_fmt', 'yuv420p',
#            '-preset', 'ultrafast',
#            '-f', 'flv',
#            'rtmp://localhost/live/output']
# p = subprocess.Popen(command, stdin=subprocess.PIPE)

# Start event loop in an external thread
# TODO: I don't know how to make it stop when I press Ctrl+C :( 
#       For now, close terminal window
loop = asyncio.new_event_loop()
def side_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
thread = Thread(target=side_thread, args=(loop,))
thread.start()

# Add to IPFS as an async coroutine
ipfs = ipfshttpclient.connect('/dns/localhost/tcp/5001/http')
async def save_to_ipfs(file):
    res = ipfs.add(file)
    print('{} written to {}'.format(res['Name'], res['Hash']))

# Records and saves a single chunk
def record_chunk():
    try:
        start_ts = time.time()  # seconds
        chunk_name = '{}.mp4'.format(int(start_ts * 1000))
        chunk = cv2.VideoWriter(chunk_name, fourcc, fps, (rewidth, reheight))
        while curr_ts := time.time() < start_ts + CHUNK_LENGTH:
            ret, frame = cap.read()
            reframe = cv2.resize(frame, (rewidth, reheight))

            # p.stdin.write(reframe.tobytes())
            chunk.write(reframe)

            c = cv2.waitKey(1)
            if c == 27:
                return
    finally:
        chunk.release()
        print("{} saved to file".format(chunk_name))
        return chunk_name

# Records chunks and uploads to IPFS
try:
    while cap.isOpened():
        chunk_name = record_chunk()
        asyncio.run_coroutine_threadsafe(save_to_ipfs(chunk_name), loop)
finally:
    cap.release()
    cv2.destroyAllWindows()