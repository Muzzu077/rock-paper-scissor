import cv2
import mediapipe as mp
import numpy as np
import random
import time

class RockPaperScissorsGame:
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
        
        # Game variables
        self.player_score = 0
        self.computer_score = 0
        self.round_count = 0
        self.game_state = "waiting"  # waiting, playing, result, countdown
        self.player_gesture = None
        self.computer_gesture = None
        self.round_winner = None
        self.countdown_timer = 0
        self.last_gesture_time = 0
        self.gesture_cooldown = 2.0  # seconds
        
        # Gesture definitions
        self.gestures = ["rock", "paper", "scissors"]
        
        # Colors for UI
        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255)
        }
    
    def get_gesture(self, hand_landmarks):
        """Determine gesture based on hand landmarks"""
        if not hand_landmarks:
            return None
            
        # Get finger tip and pip (middle joint) y-coordinates
        # MediaPipe hand landmarks: 8=index tip, 12=middle tip, 16=ring tip, 20=pinky tip
        # MediaPipe hand landmarks: 6=index pip, 10=middle pip, 14=ring pip, 18=pinky pip
        
        # Check if fingers are extended (tip y < pip y)
        index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        middle_extended = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
        ring_extended = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
        pinky_extended = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
        
        # Thumb extended (4=tip, 3=pip)
        thumb_extended = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
        
        # Gesture classification
        if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return "rock"  # All fingers closed
        elif index_extended and middle_extended and not ring_extended and not pinky_extended:
            return "scissors"  # Only index and middle extended
        elif index_extended and middle_extended and ring_extended and pinky_extended:
            return "paper"  # All fingers extended
        
        return None
    
    def determine_winner(self, player_gesture, computer_gesture):
        """Determine the winner of the round"""
        if player_gesture == computer_gesture:
            return "tie"
        
        winning_combinations = {
            "rock": "scissors",
            "paper": "rock", 
            "scissors": "paper"
        }
        
        if winning_combinations[player_gesture] == computer_gesture:
            return "player"
        else:
            return "computer"
    
    def update_scores(self, winner):
        """Update scores based on round winner"""
        if winner == "player":
            self.player_score += 1
        elif winner == "computer":
            self.computer_score += 1
    
    def draw_ui(self, frame, hand_landmarks):
        """Draw the game UI on the frame"""
        height, width = frame.shape[:2]
        
        # Draw hand landmarks
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=self.colors["blue"], thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=self.colors["yellow"], thickness=2)
            )
        
        # Draw scores
        cv2.putText(frame, f"Player: {self.player_score}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["green"], 2)
        cv2.putText(frame, f"Computer: {self.computer_score}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["red"], 2)
        cv2.putText(frame, f"Round: {self.round_count}", (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["white"], 2)
        
        # Draw game state
        if self.game_state == "waiting":
            cv2.putText(frame, "Show your gesture!", (width//2 - 150, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.colors["yellow"], 3)
            
        elif self.game_state == "playing":
            if self.player_gesture:
                cv2.putText(frame, f"Your move: {self.player_gesture.upper()}", 
                           (width//2 - 150, height//2 - 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["green"], 2)
                cv2.putText(frame, f"Computer: {self.computer_gesture.upper()}", 
                           (width//2 - 150, height//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors["red"], 2)
                
        elif self.game_state == "result":
            # Draw result
            if self.round_winner == "player":
                result_text = "YOU WIN!"
                color = self.colors["green"]
            elif self.round_winner == "computer":
                result_text = "COMPUTER WINS!"
                color = self.colors["red"]
            else:
                result_text = "IT'S A TIE!"
                color = self.colors["yellow"]
            
            cv2.putText(frame, result_text, (width//2 - 150, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
            
        elif self.game_state == "countdown":
            cv2.putText(frame, f"Next round in: {int(self.countdown_timer)}", 
                       (width//2 - 150, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.colors["white"], 3)
        
        # Draw instructions
        cv2.putText(frame, "Press 'q' to quit, 'r' to reset", (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors["white"], 2)
    
    def run_game(self):
        """Main game loop"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Rock Paper Scissors Game Started!")
        print("Show your hand gesture to play!")
        print("Press 'q' to quit, 'r' to reset scores")
        
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
            
            current_time = time.time()
            
            # Game state machine
            if self.game_state == "waiting":
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    gesture = self.get_gesture(hand_landmarks)
                    
                    if gesture and (current_time - self.last_gesture_time) > self.gesture_cooldown:
                        self.player_gesture = gesture
                        self.computer_gesture = random.choice(self.gestures)
                        self.round_winner = self.determine_winner(self.player_gesture, self.computer_gesture)
                        self.update_scores(self.round_winner)
                        self.round_count += 1
                        self.game_state = "result"
                        self.last_gesture_time = current_time
                        
            elif self.game_state == "result":
                # Show result for 2 seconds
                if current_time - self.last_gesture_time > 2.0:
                    self.game_state = "countdown"
                    self.countdown_timer = 3.0
                    
            elif self.game_state == "countdown":
                self.countdown_timer -= 0.05  # Adjust for frame rate
                if self.countdown_timer <= 0:
                    self.game_state = "waiting"
                    self.player_gesture = None
                    self.computer_gesture = None
            
            # Draw UI
            hand_landmarks = results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None
            self.draw_ui(frame, hand_landmarks)
            
            # Display frame
            cv2.imshow('Rock Paper Scissors Game', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_game()
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
    
    def reset_game(self):
        """Reset the game scores and state"""
        self.player_score = 0
        self.computer_score = 0
        self.round_count = 0
        self.game_state = "waiting"
        self.player_gesture = None
        self.computer_gesture = None
        self.round_winner = None
        print("Game reset!")

if __name__ == "__main__":
    game = RockPaperScissorsGame()
    try:
        game.run_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Game ended!")
