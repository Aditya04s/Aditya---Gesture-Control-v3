"""
gestures.py
---------------------------------
AI Gesture Experience v6.3

Author: Shane
"""

import math


class GestureRecognizer:

    def __init__(self):

        self.PINCH_THRESHOLD = 0.045

    def distance(self, a, b):

        return math.sqrt(
            (a.x - b.x) ** 2 +
            (a.y - b.y) ** 2
        )

    def finger_up(self, tip, pip, hand):

        return hand[tip].y < hand[pip].y

    def recognize(self, hand):

        index = self.finger_up(8, 6, hand)
        middle = self.finger_up(12, 10, hand)
        ring = self.finger_up(16, 14, hand)
        pinky = self.finger_up(20, 18, hand)

        thumb = self.distance(hand[4], hand[2]) > 0.07

        pinch = self.distance(hand[4], hand[8])

        # ------------------------
        # PINCH
        # ------------------------

        if pinch < self.PINCH_THRESHOLD:
            return "PINCH"

        # ------------------------
        # CURSOR
        # ------------------------

        if index and not middle and not ring and not pinky:
            return "CURSOR"

        # ------------------------
        # SCROLL
        # ------------------------

        if index and middle and not ring and not pinky:
            return "SCROLL"

        # ------------------------
        # DRAG
        # ------------------------

        if not index and not middle and not ring and not pinky:
            return "DRAG"

        # ------------------------
        # OPEN PALM
        # ------------------------

        if index and middle and ring and pinky:
            return "OPEN"

        # ------------------------
        # SCREENSHOT
        # Thumb + Pinky
        # ------------------------

        if (
            thumb
            and pinky
            and not index
            and not middle
            and not ring
        ):
            return "SCREENSHOT"

        return "UNKNOWN"