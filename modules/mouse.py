"""
modules/mouse.py
---------------------------------
Asynchronous Threaded Mouse Controller Engine
"""

import threading
import time
import pyautogui

# Safety fallback configurations for PyAutoGUI automation
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0  # Wipes out default 0.1s UI locking lag completely!


class MouseController:
    def __init__(self):
        # Retrieve the monitor's pixel dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Thread communication variables
        self.target_x = None
        self.target_y = None
        self.is_dragging = False
        
        # Define and start the asynchronous movement worker loop
        self.running = True
        self.mouse_thread = threading.Thread(target=self._mouse_loop, daemon=True)
        self.mouse_thread.start()

    def move(self, hand_landmarks):
        """Calculates normalized screen coords and updates target position."""
        # Tracking the Index Finger Tip (Landmark 8) for pointer positioning
        index_tip = hand_landmarks[8]
        
        # Map normalized landmarks (0.0 to 1.0) out to absolute screen pixels
        self.target_x = int(index_tip.x * self.screen_w)
        self.target_y = int(index_tip.y * self.screen_h)

    def click(self):
        """Triggers a virtual primary click safely on the automation background layer."""
        # Using moveTo/click coords directly avoids thread contention blocks
        if self.target_x is not None and self.target_y is not None:
            pyautogui.click(self.target_x, self.target_y)

    def drag(self):
        """Instructs the background loop thread to engage hold lock state."""
        self.is_dragging = True

    def drag_move(self, hand_landmarks):
        """Updates targeted coordinates while drag lock states stay active."""
        self.move(hand_landmarks)

    def release(self):
        """Safely signals background thread to drop any dragging lock states down."""
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

    def scroll(self, value):
        """Fires an instant hardware scroll interaction call."""
        pyautogui.scroll(value)

    def screenshot(self):
        """Captures and saves a timed disk stamp file securely."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"\n[Worker Asset] Screen saved asynchronously out to: {filename}")

    def _mouse_loop(self):
        """Internal worker thread loop prioritizing hardware position sync execution."""
        last_x, last_y = pyautogui.position()
        
        while self.running:
            # Check if main loop dropped a fresh destination point for us
            if self.target_x is not None and self.target_y is not None:
                tx, ty = self.target_x, self.target_y
                
                # Only call hardware APIs if the tracking coordinates actually shifted
                if tx != last_x or ty != last_y:
                    if self.is_dragging:
                        # Dragging requires mouse down active drag movements
                        pyautogui.dragTo(tx, ty, button='left')
                    else:
                        # Standard pointer displacement tracking
                        pyautogui.moveTo(tx, ty)
                        
                    last_x, last_y = tx, ty
            
            # Constrain update ticks to roughly ~120Hz frequency limit to protect CPU usage
            time.sleep(0.008)

    def stop(self):
        """Stops the internal mouse driver execution thread safely."""
        self.running = False
        if self.mouse_thread.is_alive():
            self.mouse_thread.join(timeout=1.0)