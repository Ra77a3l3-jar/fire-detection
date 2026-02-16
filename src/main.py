from capture.adb_capture import ADBCapture
import cv2

cap = ADBCapture()

while True:
    frame = cap.get_frame()

    if frame is None:
        continue

    cv2.imshow("test", frame)

    if cv2.waitKey(1) == 27:
        break
