import sys
import cv2

path = sys.argv[1]
vidcap = cv2.VideoCapture(path)
success, image = vidcap.read()
count = 0
while success:
    cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
    for _ in range(31):                            # only read 1/32 frames
        success, image = vidcap.read()
    print('Read a new frame: ', success)
    count += 1
