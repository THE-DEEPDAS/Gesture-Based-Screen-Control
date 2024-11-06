import cv2  # Import OpenCV for computer vision tasks
import mediapipe as mp  # Import MediaPipe for hand tracking
import numpy as np  # Import NumPy for numerical operations
import pyautogui  # Import PyAutoGUI for controlling the mouse and keyboard
import math  # Import math for mathematical functions
import time  # Import time for time-related functions

class ZoomController:
    def __init__(self):
        # Initialize camera to take the input.
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set camera width
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set camera height
        
        # Initialize MediaPipe for hands detection
        self.mp_hands = mp.solutions.hands  # Load the hand detection module from MediaPipe
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # Set to False for real-time hand detection
            max_num_hands=1,  # Limit to detecting one hand
            min_detection_confidence=0.8,  # Confidence threshold for detection (can be adjusted)
            min_tracking_confidence=0.8  # Confidence threshold for tracking (can be adjusted)
        )
        self.mp_draw = mp.solutions.drawing_utils  # Drawing utilities for visualizing hand landmarks
        
        # Zoom control variables (added cooldown to prevent too rapid changes)
        self.pinch_start_dist = None  # Variable to store the initial pinch distance
        self.zoom_cooldown = 0.3  # Time in seconds to wait before allowing another zoom action
        self.last_zoom_time = 0  # Timestamp of the last zoom action
        self.pinch_threshold = 0.08  # Threshold to determine significant pinch changes
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = False  # Disable the fail-safe feature of PyAutoGUI

    def calculate_pinch_distance(self, hand_landmarks):
        """Calculate the distance between the thumb tip and index finger tip"""
        thumb_tip = hand_landmarks.landmark[4]  # Get the landmark for the thumb tip
        index_tip = hand_landmarks.landmark[8]  # Get the landmark for the index finger tip
        
        # Calculate Euclidean distance between thumb tip and index tip
        return math.sqrt(
            (thumb_tip.x - index_tip.x)**2 + 
            (thumb_tip.y - index_tip.y)**2
        )

    def handle_zoom_gesture(self, hand_landmarks):
        """Handle the zoom gesture based on pinch distance"""
        current_time = time.time()  # Get the current time
        pinch_distance = self.calculate_pinch_distance(hand_landmarks)  # Calculate current pinch distance
        
        # Initialize pinch start distance if not set
        if self.pinch_start_dist is None:
            self.pinch_start_dist = pinch_distance  # Set the initial pinch distance
            return
        
        # Check if enough time has passed since last zoom action
        if current_time - self.last_zoom_time > self.zoom_cooldown:
            zoom_factor = self.pinch_start_dist / pinch_distance  # Calculate zoom factor based on pinch distance
            
            # Apply zoom if change is significant (we just use keyboard combination for doing that)
            if abs(zoom_factor - 1.0) > 0.2:  # Check if the zoom factor has changed significantly
                if zoom_factor > 1.0:  # If zooming out
                    pyautogui.hotkey('ctrl', '-')  # Simulate Ctrl + - for zooming out
                else:  # If zooming in
                    pyautogui.hotkey('ctrl', '+')  # Simulate Ctrl + + for zooming in
                    
                self.last_zoom_time = current_time  # Update the last zoom time
                self.pinch_start_dist = pinch_distance  # Update pinch start distance

    def process_frame(self, frame):
        """Process each frame for hand detection and gesture recognition"""
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally for mirror effect
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame to RGB format for MediaPipe
        results = self.hands.process(rgb_frame)  # Process the RGB frame for hand landmarks
        
        if results.multi_hand_landmarks:  # Check if any hands are detected
            hand_landmarks = results.multi_hand_landmarks[0]  # Get the landmarks for the first detected hand
            
            # Draw hand landmarks with blue color scheme
            self.mp_draw.draw_landmarks (
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
            
            # Process zoom gesture
            self.handle_zoom_gesture(hand_landmarks)
        else:
            self.pinch_start_dist = None  # Reset pinch start distance if no hands are detected
            
        return frame

    def run(self):
        """Main loop for the zoom controller"""
        try:
            print("Zoom Control Started!!")
            while True:
                ret, frame = self.cap.read()  # Read a frame from the camera
                if not ret:
                    break
                
                processed_frame = self.process_frame(frame)  # Process the frame for hand detection and gesture recognition
                
                # Add text overlay for instructions
                cv2.putText(processed_frame, "Zoom Control Mode - Pinch to zoom in/out",
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                cv2.imshow('Zoom Gesture Control', processed_frame)  # Display the processed frame
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            self.cleanup()  # Clean up resources when the program exits

    def cleanup(self):
        """Standard cleanup function"""
        self.cap.release()  # Release the camera
        cv2.destroyAllWindows()  # Close all OpenCV windows

if __name__ == "__main__":
    controller = ZoomController()  # Create an instance of the ZoomController class
    controller.run()  # Start the zoom controller