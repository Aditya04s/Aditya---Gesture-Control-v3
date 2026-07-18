"""
renderer.py
--------------------
AI Gesture Experience v3.1.3

Custom Hand Renderer

Author: Shane
"""

import cv2

# -----------------------------
# HAND CONNECTIONS
# -----------------------------
HAND_CONNECTIONS = [

    # Thumb
    (0,1),(1,2),(2,3),(3,4),

    # Index
    (0,5),(5,6),(6,7),(7,8),

    # Middle
    (0,9),(9,10),(10,11),(11,12),

    # Ring
    (0,13),(13,14),(14,15),(15,16),

    # Pinky
    (0,17),(17,18),(18,19),(19,20),

    # Palm
    (5,9),
    (9,13),
    (13,17)
]

# -----------------------------
# FINGER COLORS (BGR)
# -----------------------------
FINGER_COLORS = {

    "thumb":  (255, 0, 0),      # Blue
    "index":  (0, 255, 0),      # Green
    "middle": (0, 255, 255),    # Yellow
    "ring":   (0, 165, 255),    # Orange
    "pinky":  (255, 0, 255),    # Purple
    "palm":   (255, 255, 255)   # White
}


class Renderer:

    def __init__(self):

        self.debug = True

    def draw_hand(self, frame, hand_landmarks):

        h, w, _ = frame.shape

        points = []

        # -----------------------------
        # Convert landmarks to pixels
        # -----------------------------
        for lm in hand_landmarks:

            x = int(lm.x * w)
            y = int(lm.y * h)

            points.append((x, y))

        # -----------------------------
        # Draw Connections
        # -----------------------------
        for start, end in HAND_CONNECTIONS:

            cv2.line(
                frame,
                points[start],
                points[end],
                (180, 180, 180),
                2
            )

        # -----------------------------
        # Draw Wrist
        # -----------------------------
        cv2.circle(
            frame,
            points[0],
            8,
            FINGER_COLORS["palm"],
            -1
        )

        # -----------------------------
        # Thumb
        # -----------------------------
        for i in [1,2,3,4]:

            cv2.circle(
                frame,
                points[i],
                7,
                FINGER_COLORS["thumb"],
                -1
            )

        # -----------------------------
        # Index
        # -----------------------------
        for i in [5,6,7,8]:

            cv2.circle(
                frame,
                points[i],
                7,
                FINGER_COLORS["index"],
                -1
            )

        # -----------------------------
        # Middle
        # -----------------------------
        for i in [9,10,11,12]:

            cv2.circle(
                frame,
                points[i],
                7,
                FINGER_COLORS["middle"],
                -1
            )

        # -----------------------------
        # Ring
        # -----------------------------
        for i in [13,14,15,16]:

            cv2.circle(
                frame,
                points[i],
                7,
                FINGER_COLORS["ring"],
                -1
            )

        # -----------------------------
        # Pinky
        # -----------------------------
        for i in [17,18,19,20]:

            cv2.circle(
                frame,
                points[i],
                7,
                FINGER_COLORS["pinky"],
                -1
            )

        # -----------------------------
        # Highlight Fingertips
        # -----------------------------
        fingertips = [4, 8, 12, 16, 20]

        for tip in fingertips:

            cv2.circle(
                frame,
                points[tip],
                11,
                (255,255,255),
                2
            )

        # -----------------------------
        # Landmark Numbers (Debug Mode)
        # -----------------------------
        if self.debug:

            for idx, point in enumerate(points):

                cv2.putText(
                    frame,
                    str(idx),
                    (point[0]+6, point[1]-6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255,255,255),
                    1
                )