"""
detector.py
------------
AI Gesture Experience v3.1.1

Responsibilities:
- Load the MediaPipe Hand Landmarker model
- Open and manage the webcam
- Detect hands in each frame
- Cleanly release camera resources

Author: Shane
"""

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandDetector:
    """
    Handles all hand detection using the MediaPipe Tasks API.
    """

    def __init__(self):

        # -----------------------------
        # AI MODEL
        # -----------------------------
        self.model_path = "models/hand_landmarker.task"

        base_options = python.BaseOptions(
            model_asset_path=self.model_path
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,

            # Detect one hand for now
            num_hands=1,

            # Detection settings
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,

            # Webcam stream
            running_mode=vision.RunningMode.VIDEO
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

        # -----------------------------
        # CAMERA
        # -----------------------------
        self.cap = cv2.VideoCapture(0)

        # Camera Resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def detect(self, frame, timestamp):
        """
        Detect hands in a webcam frame.

        Parameters
        ----------
        frame : numpy.ndarray
            Frame captured from OpenCV.

        timestamp : int
            Timestamp in milliseconds.

        Returns
        -------
        HandLandmarkerResult
        """

        # OpenCV uses BGR
        # MediaPipe expects RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert frame to MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Detect hands
        results = self.detector.detect_for_video(
            mp_image,
            timestamp
        )

        return results

    def release(self):
        """
        Release camera resources.
        """

        if self.cap.isOpened():
            self.cap.release()