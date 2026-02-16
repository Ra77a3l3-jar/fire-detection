from capture.adb_capture import ADBCapture
from detection.yolo_detector import Detector
import cv2

cap = ADBCapture()
detector = Detector()

while True:
    frame = cap.get_frame()

    if frame is None:
        continue

    detections = detector.detect(frame)

    print(detections)

    cv2.imshow("test", frame)

    if cv2.waitKey(1) == 27:
        break
