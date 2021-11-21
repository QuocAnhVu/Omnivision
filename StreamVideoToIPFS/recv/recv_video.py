#! /usr/bin/python
import cv2
import os
import subprocess
import json
import ipfshttpclient

def init_ffmpeg(cap):
  # Get input video dimensions
  fps = int(cap.get(cv2.CAP_PROP_FPS))
  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  ffmpeg_cmd = ['ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'flv',
            'rtmp://localhost/live/output']
  return subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

try:
  TMP = './tmp/recv/'
  if not os.path.exists(TMP):
    os.makedirs(TMP)
  vids = [TMP + f for f in os.listdir(TMP) if os.path.isfile(os.path.join(TMP, f))]
  for vid in vids:
    os.remove(vid)

  ffmpeg = None
  recv_node = subprocess.Popen("go run recv/recv_node.go".split(), stdout=subprocess.PIPE)
  ipfs = ipfshttpclient.connect()

  for line in recv_node.stdout:
    # read msg from p2p node
    # msg is {source, timestamp, address}
    msg = json.loads(line)
    ipfs.get(msg['address'], target=TMP)
    vid = [TMP + f for f in os.listdir(TMP) if os.path.isfile(os.path.join(TMP, f))][0]

    # load video into opencv
    cap = cv2.VideoCapture(vid)
    if ffmpeg is None:
      ffmpeg = init_ffmpeg(cap)

    # stream video to RTMP
    while cap.isOpened():
      ret, frame = cap.read()
      if not ret:
        break
      ffmpeg.stdin.write(frame.tobytes())
    
    # remove video
    os.remove(vid)
finally:
  recv_node.terminate()
  ffmpeg.terminate()