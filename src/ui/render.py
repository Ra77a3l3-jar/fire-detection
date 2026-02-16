import cv2

class Render:
    def draw(self, frame, detections):

        output = frame.copy()

        for detec in detections:
            x1, y1, x2, y2 = detec["box"]
            confidence = detec["confidence"]

            # Bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 2)


            # lable
            lable = f"FIRE {confidence*100:.1f}%"            
            cv2.putText(
                output,
                lable,
                (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )

        return output
