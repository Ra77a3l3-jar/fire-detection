import cv2

class Render:
    def __init__(self) -> None:
        # Colors
        self.FIRE = (0, 69, 255)
        self.ALLERT = (0, 0, 255)
        self.GREY = (40, 40, 40)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (0, 165, 255)
    
    def draw(self, frame, detections):

        output = frame.copy()

        for detec in detections:
            x1, y1, x2, y2 = detec["box"]
            confidence = detec["confidence"]

            # Filled background for better visibility
            overlay = output.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), self.FIRE, -1)
            cv2.addWeighted(overlay, 0.2, output, 0.8, 0, output)

            # Bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), self.FIRE, 3)
            cv2.rectangle(output, (x1-2, y1-2), (x2+2, y2+2), (0, 100, 255), 1)

            # Fire lable with background
            lable = f"FIRE {confidence*100:.1f}%"
            (lable_w, lable_h), baseline = cv2.getTextSize(
                lable, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )

            # Fire lable box
            cv2.rectangle(
                output,
                (x1, y1 - lable_h - baseline - 10),
                (x1 + lable_w + 10, y1),
                self.FIRE,
                -1
            )

            # Lable text in box
            cv2.putText(
                output,
                lable,
                (x1 + 5, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                self.WHITE,
                2,
                cv2.LINE_AA
            )

        return output
