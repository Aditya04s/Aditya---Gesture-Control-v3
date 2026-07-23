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
        # self.cap = cv2.VideoCapture(0)
        
        # 1. Initialize the camera
        self.cap = cv2.VideoCapture(0)
        
        # 2. Define target resolutions (Highest to lowest fallback)
        target_resolutions = [
            (1920, 1080),
            (1280, 720),
            (960, 540),
            (640, 480)
        ]
        
        # 3. Hunt for the highest supported native resolution
        for width, height in target_resolutions:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Read back from the driver to confirm if the setting was accepted
            actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            if actual_w == width and actual_h == height:
                print(f"\n[Camera] Hardware locked at native resolution: {int(actual_w)}x{int(actual_h)}")
                break
        # =====================================================================
        # 4. NEW: FPS NEGOTIATION
        # =====================================================================
        # You can change this target anytime. 60 is the golden standard for smooth tracking.
        self.target_fps = 120
        
        # Ask the camera driver to run at the target speed
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Read back what the hardware actually allowed us to use safely
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"[Camera] Hardware FPS negotiated and locked at: {actual_fps}")
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