import cv2
import mediapipe as mp
import numpy as np
import math

class GestureTester:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Colors for visualization
        self.colors = {
            "white": (255, 255, 255),
            "green": (0, 255, 0),
            "red": (0, 0, 255),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255)
        }
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def get_gesture(self, hand_landmarks):
        """Test gesture detection function"""
        if not hand_landmarks:
            return None, 0
            
        # Get key landmarks
        wrist = hand_landmarks.landmark[0]
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]
        
        # Get finger pip (middle joint) landmarks
        thumb_pip = hand_landmarks.landmark[3]
        index_pip = hand_landmarks.landmark[6]
        middle_pip = hand_landmarks.landmark[10]
        ring_pip = hand_landmarks.landmark[14]
        pinky_pip = hand_landmarks.landmark[18]
        
        # Calculate finger extension with tolerance
        tolerance = 0.02
        
        index_extended = index_tip.y < (index_pip.y - tolerance)
        middle_extended = middle_tip.y < (middle_pip.y - tolerance)
        ring_extended = ring_tip.y < (ring_pip.y - tolerance)
        pinky_extended = pinky_tip.y < (pinky_pip.y - tolerance)
        
        # Thumb detection
        thumb_extended = self.calculate_distance(thumb_tip, wrist) > self.calculate_distance(thumb_pip, wrist)
        
        # Debug information
        debug_info = {
            "index": index_extended,
            "middle": middle_extended,
            "ring": ring_extended,
            "pinky": pinky_extended,
            "thumb": thumb_extended
        }
        
        # Gesture classification
        gesture = None
        confidence = 0.0
        
        if (not index_extended and not middle_extended and 
            not ring_extended and not pinky_extended):
            gesture = "rock"
            confidence = 0.9
        elif (index_extended and middle_extended and 
              not ring_extended and not pinky_extended):
            gesture = "scissors"
            confidence = 0.85
        elif (index_extended and middle_extended and 
              ring_extended and pinky_extended):
            gesture = "paper"
            confidence = 0.9
        
        return gesture, confidence, debug_info
    
    def draw_debug_info(self, frame, hand_landmarks, gesture, confidence, debug_info):
        """Draw debug information on the frame"""
        height, width = frame.shape[:2]
        
        # Draw hand landmarks
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=self.colors["blue"], thickness=2, circle_radius=3),
                self.mp_drawing.DrawingSpec(color=self.colors["yellow"], thickness=2)
            )
        
        # Draw gesture information
        if gesture:
            cv2.putText(frame, f"Detected: {gesture.upper()}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["green"], 2)
            cv2.putText(frame, f"Confidence: {confidence:.1%}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["yellow"], 2)
        else:
            cv2.putText(frame, "No gesture detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["red"], 2)
        
        # Draw finger status
        y_offset = 110
        for finger, status in debug_info.items():
            color = self.colors["green"] if status else self.colors["red"]
            status_text = "EXTENDED" if status else "CLOSED"
            cv2.putText(frame, f"{finger.capitalize()}: {status_text}", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30
        
        # Draw instructions
        cv2.putText(frame, "Show hand gestures to test detection", (10, height - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors["white"], 2)
        cv2.putText(frame, "Press 'q' to quit", (10, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors["white"], 2)
        
        # Draw gesture examples
        cv2.putText(frame, "Rock: Fist | Paper: Open Palm | Scissors: Peace Sign", 
                   (width//2 - 200, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["white"], 1)
    
    def run_test(self):
        """Run the gesture testing application"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Gesture Testing Started!")
        print("Show different hand gestures to test detection")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            gesture = None
            confidence = 0.0
            debug_info = {}
            
            # Process hand landmarks
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                gesture, confidence, debug_info = self.get_gesture(hand_landmarks)
            
            # Draw debug information
            self.draw_debug_info(frame, 
                               results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None,
                               gesture, confidence, debug_info)
            
            # Display frame
            cv2.imshow('Gesture Testing', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

if __name__ == "__main__":
    tester = GestureTester()
    try:
        tester.run_test()
    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Testing ended!")
