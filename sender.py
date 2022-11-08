import cv2
#import time
import subprocess as sp
import glob
import os

cap = cv2.VideoCapture(0)

# For NVIDIA using NVMM memory
#cap = cv2.VideoCapture("udpsrc port=5000 ! application/x-rtp,media=video,encoding-name=H264 ! queue ! rtpjitterbuffer latency=500 ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! queue ! appsink drop=1", cv2.CAP_GSTREAMER)

img_width = 1920
img_height = 1080

ffmpeg_cmd = 'ffmpeg'
ffplay_cmd = 'ffplay'

img_list = glob.glob("*.jpg")
img_list_len = len(img_list)
img_index = 0

fps = 5

# rtsp_server = 'rtsp://localhost:31415/live.stream'
rtp_server = 'rtp://localhost:31415/live.stream'
udp = "udp://239.0.0.1:1234?ttl=13"
# You will need to start the server up first, before the sending client (when using TCP). See: https://trac.ffmpeg.org/wiki/StreamingGuide#Pointtopointstreaming
ffplay_process = sp.Popen([ffplay_cmd, 
    '-fflags', 'nobuffer', 
    '-flags', 'low_delay', 
    '-strict', 'experimental', 
    udp])  # Use FFplay sub-process for receiving the RTSP video.


command = [ffmpeg_cmd,
           '-f', 'rawvideo',  # Apply raw video as input - it's more efficient than encoding each frame to PNG
           '-s', f'{img_width}x{img_height}',
           '-pixel_format', 'bgr24',
           '-i', '-',
           '-pix_fmt', 'yuv420p',
           '-preset', 'medium',
           '-profile', 'high',
           '-vcodec', 'libx264',
           '-minrate', '2000K',
           '-maxrate', '2000K',
           '-tune', 'zerolatency',
           '-f', 'mpegts',
           #'-muxdelay', '0.1',
           udp]

process = sp.Popen(command, stdin=sp.PIPE)  # Execute FFmpeg sub-process for RTSP streaming

while True:
    ret_val, img = cap.read()
    process.stdin.write(img.tobytes())  # Write raw frame to stdin pipe.

    key = cv2.waitKey(1)
    if key == ord("q"):
        break


process.stdin.close()  # Close stdin pipe
process.wait()  # Wait for FFmpeg sub-process to finish
ffplay_process.kill()  # Forcefully close FFplay sub-process
cv2.destroyAllWindows()  # Close OpenCV window