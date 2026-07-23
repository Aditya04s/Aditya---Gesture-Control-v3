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
from modules.scroll import ScrollManager # <--- NEW IMPORT

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
    scroll_manager = ScrollManager(mouse) # <--- NEW INITIALIZATION

    previous_time = time.time()
    last_scroll_y = None

    # =====================================================================
    # WINDOW SETUP
    # =====================================================================
    window_name = "AI Gesture Experience"
    # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # (The line with cv2.setWindowProperty forcing FULLSCREEN has been removed)

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

            # ----------------------------
            # CLICK / DOUBLE CLICK
            # ----------------------------
            elif gesture_name == "PINCH":
                mouse.release()
                mouse.click()

            elif gesture_name == "DOUBLE_CLICK":
                mouse.release()
                mouse.double_click()

            elif gesture_name == "DRAG":
                mouse.drag()
                # Use move() so it utilizes your Active Control Region (ACR) clamping!
                mouse.move(hand) 

            elif gesture_name == "SCROLL":
                mouse.release()
                # Cursor naturally freezes because mouse.move() is bypassed!
                # Logic is handled completely by the update call below
                # y = hand[8].y
                # if last_scroll_y is not None:
                #     diff = last_scroll_y - y
                #     if abs(diff) > 0.015:
                #         mouse.scroll(int(diff * 900))
                # last_scroll_y = y

            elif gesture_name == "SCREENSHOT":
                mouse.release()
                # NEW: Tell the state engine to trigger. It manages its own cooldown locks!
                shot_manager.trigger()
                # last_scroll_y = None
            
            else:
                # Handles "UNKNOWN" safety freezing
                mouse.release()
                # last_scroll_y = None
        else:
            # Handles "NO HAND" lost tracking
            mouse.release()
            # last_scroll_y = None

        current = time.time()
        fps = 1 / (current - previous_time)
        previous_time = current

        # NEW: Give the state manager a clock pulse once per frame loop execution
        # CLOCK PULSES: Update state managers every frame
        shot_manager.update()

        # NEW: Feed the scroll manager the current gesture state and hand map
        is_scrolling = (gesture_name == "SCROLL")
        if results.hand_landmarks:
            scroll_manager.update(is_scrolling, hand)
        else:
            scroll_manager.update(False, None)

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
        # elif shot_manager.state == ScreenshotState.NOTIFICATION:
        #     cv2.putText(
        #         frame, 
        #         "Screenshot Saved!", 
        #         (380, 650), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3
        #     )

        # 3. Render Green Text notification save confirm
        elif shot_manager.state == ScreenshotState.NOTIFICATION:
            cv2.putText(frame, "Screenshot Saved!", (380, 650), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        # 4. Render Scroll HUD
        if scroll_manager.is_active:
            cv2.putText(
                frame, 
                f"SCROLL MODE | Speed: {scroll_manager.current_speed} | Dir: {scroll_manager.direction}", 
                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )

        ui.draw(frame, fps, gesture_name, confidence, "NORMAL")

        # =====================================================================
        # ACTIVE CONTROL REGION (ACR) DEBUG RENDERER
        # =====================================================================
        # Get current frame dimensions dynamically
        h, w, c = frame.shape
        
        # Calculate pixel coordinates for the ACR bounds using the mouse config
        margin_x_px = int(w * mouse.margin_x)
        margin_y_px = int(h * mouse.margin_y)
        
        # Draw a yellow rectangle to visualize the active tracking area
        # Draw a yellow rectangle to visualize the active tracking area
        cv2.rectangle(
            frame, 
            (margin_x_px, margin_y_px), 
            (w - margin_x_px, h - margin_y_px), 
            (0, 255, 255), 
            2
        )

        ui.draw(frame, fps, gesture_name, confidence, "NORMAL")
        
        # CHANGED: Use the variable here instead of the hardcoded string
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Clean shutdown of tracking and background operations
    mouse.stop()   # NEW: Disengages the background mouse looping threads safely
    worker.stop()
    detector.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()