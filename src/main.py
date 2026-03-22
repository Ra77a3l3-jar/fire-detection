import cv2
import config

from detection.yolo_detector import YOLODetector
from detection.aruco_detector import ARUCODetector
from ui.render import Render
from logic.controller import DetectionController
from utils.evidence_saver import EvidenceSaver
from utils.utils import full_inside, iou

cap = cv2.VideoCapture(config.VIDEO_SOURCE)

detector = YOLODetector()
aruco = ARUCODetector()
renderer = Render()
controller = DetectionController()
saver = EvidenceSaver()

PHASE = 1
rover_streak = 0

cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)

while True:

    ret, frame =cap.read()
    if not ret or frame is None:
        continue

    if PHASE == 1:
        detections = detector.detect(frame)
        alert = controller.process(detections)

        # Draw detections first
        frame = renderer.draw(frame, detections)

        # Draw info panel with status
        frame = renderer.draw_info(
            frame,
            controller.fps,
            controller.total_detections,
            detector.device,
            fire_alert=alert
        )

        if alert:
            print("FIRE CONFIRMED")
            PHASE = 2

            if config.SAVE_EVIDENCE:
                path = saver.save(frame)
                print(f"Fire Saved -> {path}")

    elif PHASE == 2:

        fire_detection = detector.detect(frame)

        fire_box = None

        for detec in fire_detection:
            x1, y1, x2, y2 = detec["box"]
            area = (x2 - x1) * (y2 - y1)

            if area >= config.MIN_FIRE_AREA:
                fire_box = detec["box"]
                break

        # Fire box
        frame = renderer.draw(frame, fire_detection)

        rover_box = aruco.detect(frame)

        if fire_box and rover_box:
            inside = full_inside(rover_box, fire_box)
            overlap = iou(rover_box, fire_box)

            if inside or overlap > config.MIN_OVERLAP_AREA  :
                rover_streak += 1
            else:
                rover_streak = 0

            if rover_streak >= config.ROVER_CONFIRM_FRAMES:
                print("COMPLETED")
                break

            x1, y1, x2, y2 = rover_box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
