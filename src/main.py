import cv2
import numpy as numpy
import subprocess

process = subprocess.Popen(['adb', 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE)
img = process.stdout.read()
frame = cv2.imdecode(numpy.frombuffer(img, numpy.uint8), cv2.IMREAD_COLOR)
cv2.imshow('test frame', frame)
cv2.waitKey(0)
