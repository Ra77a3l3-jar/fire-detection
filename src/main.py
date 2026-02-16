from capture.adb_capture import ADBCapture
from detection.yolo_detector import Detector
from ui.render import Render
from logic.controller import DetectionController
from utils.evidence_saver import EvidenceSaver
import cv2


def resize_for_display(frame, max_width=900):
    h, w = frame.shape[:2]

    if w <= max_width:
        return frame

    scale = max_width / w
    return cv2.resize(frame, None, fx=scale, fy=scale)


cap = ADBCapture()
detector = Detector()
renderer = Render()
controller = DetectionController(confirm_frames=3)
saver = EvidenceSaver()

cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)

while True:
    frame = cap.get_frame()

    if frame is None:
        continue

    detections = detector.detect(frame)
    alert = controller.process(detections)
    frame = renderer.draw(frame, detections)

    cv2.putText(
        frame,
        f"FPS: {controller.fps:.1f} | Detections: {controller.total_detections}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        4
    )

    if alert:
        print("FIRE CONFIRMED")

        path = saver.save(frame)
        print(f"Fire captured and saved -> {path}")

        cv2.putText(
            frame,
            "FIRE DETECTED",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            4,
            (0, 0, 255),
            4
        )

    display = resize_for_display(frame)

    cv2.imshow("Fire Detector", display)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
