"""
main.py
---------------------------------
AI Gesture Experience v6.3 (State Machine Architecture)
"""

import cv2
import time

from modules.detector import HandDetector
from modules.renderer import Renderer
from modules.motion import MotionEngine
from modules.gestures import GestureRecognizer
from modules.mouse import MouseController
from modules.ui import UI
from modules.worker import BackgroundWorker
# NEW: Import our State Manager and the Enum states
from modules.screenshot import ScreenshotManager, ScreenshotState


def main():
    detector = HandDetector()
    renderer = Renderer()
    motion = MotionEngine()
    gesture = GestureRecognizer()
    mouse = MouseController()
    ui = UI()
    worker = BackgroundWorker()
    
    # NEW: Instantiate the state manager, passing dependencies directly
    shot_manager = ScreenshotManager(worker, mouse)

    previous_time = time.time()
    last_scroll_y = None

    while True:
        success, frame = detector.cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        timestamp = int(time.time() * 1000)
        results = detector.detect(frame, timestamp)

        gesture_name = "NO HAND"
        confidence = 100

        if results.hand_landmarks:
            hand = motion.smooth(results.hand_landmarks[0])
            renderer.draw_hand(frame, hand)
            gesture_name = gesture.recognize(hand)

            if gesture_name == "CURSOR":
                mouse.release()
                mouse.move(hand)
                last_scroll_y = None

            elif gesture_name == "PINCH":
                mouse.release()
                mouse.click()
                last_scroll_y = None

            elif gesture_name == "DRAG":
                mouse.drag()
                mouse.drag_move(hand)
                last_scroll_y = None

            elif gesture_name == "SCROLL":
                mouse.release()
                y = hand[8].y
                if last_scroll_y is not None:
                    diff = last_scroll_y - y
                    if abs(diff) > 0.015:
                        mouse.scroll(int(diff * 900))
                last_scroll_y = y

            elif gesture_name == "SCREENSHOT":
                mouse.release()
                # NEW: Tell the state engine to trigger. It manages its own cooldown locks!
                shot_manager.trigger()
                last_scroll_y = None
        else:
            mouse.release()
            last_scroll_y = None

        current = time.time()
        fps = 1 / (current - previous_time)
        previous_time = current

        # NEW: Give the state manager a clock pulse once per frame loop execution
        shot_manager.update()

        # =====================================================================
        # STATE RENDERING CORNER (main.py only reads state, never modifies it)
        # =====================================================================
        
        # 1. Render Countdown overlay
        if shot_manager.state == ScreenshotState.COUNTDOWN:
            cv2.putText(
                frame, 
                str(shot_manager.current_countdown_value), 
                (560, 360), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 8
            )

        # 2. Render White screen Flash mix
        elif shot_manager.state == ScreenshotState.FLASH:
            flash_frame = frame.copy()
            flash_frame[:] = 255
            frame = cv2.addWeighted(flash_frame, 0.8, frame, 0.2, 0)

        # 3. Render Green Text notification save confirm
        elif shot_manager.state == ScreenshotState.NOTIFICATION:
            cv2.putText(
                frame, 
                "Screenshot Saved!", 
                (380, 650), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3
            )

        ui.draw(frame, fps, gesture_name, confidence, "NORMAL")
        cv2.imshow("AI Gesture Experience", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Clean shutdown of tracking and background operations
    mouse.stop()   # NEW: Disengages the background mouse looping threads safely
    worker.stop()
    detector.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()