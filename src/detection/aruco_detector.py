import cv2
import numpy as np
import config

class ARUCODetector:

    def __init__ (self) -> None:
        aruco_dict = getattr(cv2, config.ARUCO_DICTIONARY_NAME)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict)
        self.parameters = cv2.aruco.DetectorParameters()

    def detect(self, frame):

        corners, ids, _ = cv2.aruco.detectMarkers(
            frame,
            self.aruco_dict,
            parameters=self.parameters
        )

        if ids is None:
            return None
