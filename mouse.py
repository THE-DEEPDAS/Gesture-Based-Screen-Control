import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from math import hypot

class GestureMouseController:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Screen settings
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.FAILSAFE = False
        
        # Initialize state variables
        self.prev_x = self.prev_y = None
        self.prev_index_y = None
        self.last_click_time = 0
        self.click_cooldown = 0.3  # seconds
        
        # Smoothing parameters
        self.smooth_x = self.smooth_y = 0
        self.smoothing = 0.5
        
        # Frame processing
        self.frame_reduction = 50
        
        # Enhanced scroll settings
        self.scroll_speed = 15
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.05
        self.scroll_buffer = []
        self.max_buffer_size = 5

    def calculate_distance(self, p1, p2):
        return hypot(p1.x - p2.x, p1.y - p2.y)

    def get_finger_states(self, hand_landmarks):
        """Determine which fingers are up."""
        fingers = []
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]
        fingers.append((thumb_tip.x < thumb_ip.x))  # Thumb
        
        tips = [8, 12, 16, 20]
        for tip in tips:
            fingers.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y)
        return fingers

    def handle_mouse_movement(self, hand_landmarks, frame_shape):
        """Hovering logic."""
        index_tip = hand_landmarks.landmark[8]
        x = int(index_tip.x * frame_shape[1])
        y = int(index_tip.y * frame_shape[0])
        
        if self.prev_x is None:
            self.prev_x, self.prev_y = x, y
            self.smooth_x, self.smooth_y = x, y
            return

        target_x = np.interp(x, (self.frame_reduction, frame_shape[1] - self.frame_reduction), 
                            (0, self.screen_width))
        target_y = np.interp(y, (self.frame_reduction, frame_shape[0] - self.frame_reduction), 
                            (0, self.screen_height))
        
        self.smooth_x = int(self.smooth_x * self.smoothing + target_x * (1 - self.smoothing))
        self.smooth_y = int(self.smooth_y * self.smoothing + target_y * (1 - self.smoothing))
        
        pyautogui.moveTo(self.smooth_x, self.smooth_y)
        self.prev_x, self.prev_y = x, y

    def handle_click(self):
        """Clicking logic."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = current_time

    def handle_scrolling(self, hand_landmarks, frame_shape):
        """Enhanced scrolling with pressure/intensity-based sensitivity."""
        current_time = time.time()
        if current_time - self.last_scroll_time < self.scroll_cooldown:
            return
            
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        
        # Calculate finger separation as a proxy for "pressure"
        finger_distance = self.calculate_distance(index_tip, middle_tip)
        current_y = (index_tip.y + middle_tip.y) / 2 * frame_shape[0]
        
        # Add to rolling buffer for smooth movement detection
        self.scroll_buffer.append(current_y)
        if len(self.scroll_buffer) > self.max_buffer_size:
            self.scroll_buffer.pop(0)
        
        if len(self.scroll_buffer) >= 2:
            # Calculate moving average for smoother scrolling
            avg_movement = (self.scroll_buffer[-1] - self.scroll_buffer[0]) / len(self.scroll_buffer)
            
            # Adjust scroll speed based on finger separation (pressure proxy)
            pressure_factor = 1.0 + (0.05 - finger_distance) * 20  # Increases speed when fingers are closer
            scroll_amount = int(avg_movement * self.scroll_speed * pressure_factor)
            
            # Apply threshold to prevent accidental scrolling
            if abs(scroll_amount) > 1:
                pyautogui.scroll(scroll_amount)
                self.last_scroll_time = current_time

    def run(self):
        cap = cv2.VideoCapture(0)
        tap_threshold_y = 0.02

        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                fingers = self.get_finger_states(hand_landmarks)
                
                if fingers[1] and not fingers[2]:  # Hovering and clicking mode with index finger up only
                    index_tip = hand_landmarks.landmark[8]

                    if self.prev_index_y is not None and index_tip.y > self.prev_index_y + tap_threshold_y:
                        self.handle_click()
                    else:
                        self.handle_mouse_movement(hand_landmarks, frame.shape)

                    self.prev_index_y = index_tip.y
                
                elif fingers[1] and fingers[2]:  # Scrolling mode with both index and middle fingers up
                    self.handle_scrolling(hand_landmarks, frame.shape)
                    
            cv2.imshow('Gesture Mouse Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controller = GestureMouseController()
    controller.run()
