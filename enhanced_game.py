import cv2
import mediapipe as mp
import numpy as np
import random
import time
import math

class EnhancedRockPaperScissorsGame:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.6
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
        self.gesture_confidence = 0
        self.best_of_5_mode = False
        self.games_to_win = 3
        

        
        # Gesture definitions
        self.gestures = ["rock", "paper", "scissors"]
        
        # Enhanced color scheme with modern colors
        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255),
            "purple": (255, 0, 255),
            "orange": (0, 165, 255),
            "cyan": (255, 255, 0),
            "pink": (147, 20, 255),
            "lime": (0, 255, 127),
            "gold": (0, 215, 255),
            "silver": (192, 192, 192),
            "navy": (128, 0, 0),
            "teal": (128, 128, 0),
            "maroon": (0, 0, 128),
            "olive": (0, 128, 128)
        }
        
        # Gesture history for better detection
        self.gesture_history = []
        self.history_size = 5
        
        # Animation variables
        self.animation_timer = 0
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        
        # UI state variables
        self.show_help = False
        self.help_timer = 0
        
        # Enhanced UI elements
        self.ui_alpha = 0.0
        self.fade_direction = 1
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def get_gesture(self, hand_landmarks):
        """Enhanced gesture detection with confidence scoring"""
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
        
        # Calculate finger extension (tip y < pip y means extended)
        # Add some tolerance for better detection
        tolerance = 0.02
        
        index_extended = index_tip.y < (index_pip.y - tolerance)
        middle_extended = middle_tip.y < (middle_pip.y - tolerance)
        ring_extended = ring_tip.y < (ring_pip.y - tolerance)
        pinky_extended = pinky_tip.y < (pinky_pip.y - tolerance)
        
        # Thumb detection (more complex due to different orientation)
        thumb_extended = self.calculate_distance(thumb_tip, wrist) > self.calculate_distance(thumb_pip, wrist)
        
        # Gesture classification with confidence
        confidence = 0.0
        gesture = None
        
        # Rock: All fingers closed
        if (not index_extended and not middle_extended and 
            not ring_extended and not pinky_extended):
            gesture = "rock"
            confidence = 0.9
            if not thumb_extended:
                confidence = 0.95
        
        # Scissors: Only index and middle extended
        elif (index_extended and middle_extended and 
              not ring_extended and not pinky_extended):
            gesture = "scissors"
            confidence = 0.85
            if not thumb_extended:
                confidence = 0.9
        
        # Paper: All fingers extended
        elif (index_extended and middle_extended and 
              ring_extended and pinky_extended):
            gesture = "paper"
            confidence = 0.9
            if thumb_extended:
                confidence = 0.95
        
        # Additional confidence based on hand stability
        if gesture:
            # Check if hand is relatively stable (not moving too much)
            if len(self.gesture_history) > 0:
                last_gesture = self.gesture_history[-1]
                if last_gesture == gesture:
                    confidence += 0.05  # Bonus for consistent gesture
            
            # Ensure confidence doesn't exceed 1.0
            confidence = min(confidence, 1.0)
        
        return gesture, confidence
    
    def draw_gesture_icon(self, frame, x, y, gesture, size=60):
        """Draw a visual icon for each gesture"""
        if gesture == "rock":
            # Draw fist icon (circle)
            cv2.circle(frame, (x + size//2, y + size//2), size//2, self.colors["gold"], -1)
            cv2.circle(frame, (x + size//2, y + size//2), size//2, self.colors["white"], 2)
        elif gesture == "paper":
            # Draw paper icon (rectangle)
            cv2.rectangle(frame, (x, y), (x + size, y + size), self.colors["cyan"], -1)
            cv2.rectangle(frame, (x, y), (x + size, y + size), self.colors["white"], 2)
        elif gesture == "scissors":
            # Draw scissors icon (two lines forming V)
            cv2.line(frame, (x + 10, y + size - 10), (x + size//2, y + 10), self.colors["pink"], 4)
            cv2.line(frame, (x + size - 10, y + size - 10), (x + size//2, y + 10), self.colors["pink"], 4)
            cv2.circle(frame, (x + size//2, y + 10), 5, self.colors["white"], -1)
    
    def update_gesture_history(self, gesture):
        """Update gesture history for better detection"""
        if gesture:
            self.gesture_history.append(gesture)
            if len(self.gesture_history) > self.history_size:
                self.gesture_history.pop(0)
    
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
    
    def check_game_winner(self):
        """Check if someone has won the best of 5"""
        if self.best_of_5_mode:
            if self.player_score >= self.games_to_win:
                return "player"
            elif self.computer_score >= self.games_to_win:
                return "computer"
        return None
    
    def draw_gesture_icon(self, frame, x, y, gesture, size=60):
        """Draw a visual icon for each gesture"""
        if gesture == "rock":
            # Draw fist icon (circle)
            cv2.circle(frame, (x + size//2, y + size//2), size//2, self.colors["gold"], -1)
            cv2.circle(frame, (x + size//2, y + size//2), size//2, self.colors["white"], 2)
        elif gesture == "paper":
            # Draw paper icon (rectangle)
            cv2.rectangle(frame, (x, y), (x + size, y + size), self.colors["cyan"], -1)
            cv2.rectangle(frame, (x, y), (x + size, y + size), self.colors["white"], 2)
        elif gesture == "scissors":
            # Draw scissors icon (two lines forming V)
            cv2.line(frame, (x + 10, y + size - 10), (x + size//2, y + 10), self.colors["pink"], 4)
            cv2.line(frame, (x + size - 10, y + size - 10), (x + size//2, y + 10), self.colors["pink"], 4)
            cv2.circle(frame, (x + size//2, y + 10), 5, self.colors["white"], -1)
    
    def draw_ui(self, frame, hand_landmarks):
        """Clean, organized UI with proper spacing and no overlapping elements"""
        height, width = frame.shape[:2]
        
        # Update animation timer
        self.animation_timer += 0.05
        if self.animation_timer > 2 * np.pi:
            self.animation_timer = 0
        
        # Update pulse animation
        self.pulse_scale += 0.02 * self.pulse_direction
        if self.pulse_scale > 1.1 or self.pulse_scale < 0.9:
            self.pulse_direction *= -1
        
        # Draw hand landmarks with subtle styling
        if hand_landmarks:
            landmark_spec = self.mp_drawing.DrawingSpec(
                color=self.colors["cyan"], 
                thickness=2, 
                circle_radius=3
            )
            connection_spec = self.mp_drawing.DrawingSpec(
                color=self.colors["gold"], 
                thickness=1
            )
            
            self.mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                landmark_spec,
                connection_spec
            )
        
        # Draw clean score panel on the right side (no overlap with center)
        self.draw_clean_score_panel(frame, width, height)
        
        # Draw game state in the center with proper spacing
        self.draw_center_game_state(frame, width, height)
        
        # Draw clean instructions at the bottom
        self.draw_clean_instructions(frame, width, height)
        
        # Draw help overlay if requested
        if self.show_help:
            self.draw_help_overlay(frame)
        
        # Draw progress bar for best of 5 mode (top right)
        if self.best_of_5_mode:
            self.draw_progress_bar(frame, width, height)
    
    def draw_clean_score_panel(self, frame, width, height):
        """Draw a clean, organized score panel on the right side"""
        panel_width = 180
        panel_x = width - panel_width - 20
        panel_y = 20
        
        # Panel background with subtle transparency
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + 280), 
                     self.colors["navy"], -1)
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + 280), 
                     self.colors["white"], 2)
        
        # Player score
        score_y = panel_y + 30
        cv2.putText(frame, "PLAYER", (panel_x + 10, score_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["lime"], 2)
        cv2.putText(frame, str(self.player_score), (panel_x + 10, score_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.colors["lime"], 3)
        
        # Computer score
        score_y += 70
        cv2.putText(frame, "COMPUTER", (panel_x + 10, score_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["red"], 2)
        cv2.putText(frame, str(self.computer_score), (panel_x + 10, score_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.colors["red"], 3)
        
        # Round counter
        score_y += 70
        cv2.putText(frame, "ROUND", (panel_x + 10, score_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["white"], 2)
        cv2.putText(frame, str(self.round_count), (panel_x + 10, score_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.colors["white"], 3)
        
        # Confidence indicator (only when available)
        if self.gesture_confidence > 0:
            score_y += 70
            cv2.putText(frame, "CONFIDENCE", (panel_x + 10, score_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors["yellow"], 2)
            
            # Confidence bar
            bar_width = 150
            bar_height = 8
            bar_x = panel_x + 15
            bar_y = score_y + 20
            
            # Background
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         self.colors["black"], -1)
            
            # Filled bar
            fill_width = int(bar_width * self.gesture_confidence)
            confidence_color = self.colors["green"] if self.gesture_confidence > 0.8 else \
                             self.colors["yellow"] if self.gesture_confidence > 0.6 else self.colors["red"]
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                         confidence_color, -1)
            
            # Percentage text
            cv2.putText(frame, f"{self.gesture_confidence:.0%}", (bar_x + 60, bar_y + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors["white"], 1)
    
    def draw_center_game_state(self, frame, width, height):
        """Draw the main game state in the center with proper spacing"""
        center_x = width // 2
        center_y = height // 2
        
        if self.game_state == "waiting":
            self.draw_waiting_state(frame, center_x, center_y)
        elif self.game_state == "playing":
            self.draw_playing_state(frame, center_x, center_y)
        elif self.game_state == "result":
            self.draw_result_state(frame, center_x, center_y)
        elif self.game_state == "countdown":
            self.draw_countdown_state(frame, center_x, center_y)
        
        # Check for game winner
        game_winner = self.check_game_winner()
        if game_winner:
            self.draw_game_winner(frame, center_x, center_y, game_winner)
    
    def draw_waiting_state(self, frame, center_x, center_y):
        """Draw clean waiting state"""
        # Main instruction box
        box_width = 350
        box_height = 100
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2
        
        # Clean background
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["navy"], -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["cyan"], 3)
        
        # Instruction text
        cv2.putText(frame, "Show your gesture!", (box_x + 50, box_y + 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.colors["white"], 3)
        
        # Gesture examples below (smaller and organized)
        examples_y = box_y + box_height + 20
        for i, gesture in enumerate(self.gestures):
            icon_x = box_x + i * 110
            self.draw_gesture_icon(frame, icon_x, examples_y, gesture, 40)
            
            # Gesture name
            cv2.putText(frame, gesture.upper(), (icon_x + 10, examples_y + 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors["white"], 1)
    
    def draw_playing_state(self, frame, center_x, center_y):
        """Draw clean playing state"""
        if not self.player_gesture:
            return
            
        # Moves comparison box
        box_width = 400
        box_height = 120
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2
        
        # Clean background
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["purple"], -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["white"], 2)
        
        # Player move (left)
        player_x = box_x + 30
        player_y = box_y + 30
        self.draw_gesture_icon(frame, player_x, player_y, self.player_gesture, 60)
        cv2.putText(frame, "YOU", (player_x + 15, player_y + 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["lime"], 2)
        
        # VS text
        vs_x = center_x - 20
        vs_y = center_y + 10
        cv2.putText(frame, "VS", (vs_x, vs_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.colors["gold"], 3)
        
        # Computer move (right)
        computer_x = box_x + box_width - 90
        computer_y = box_y + 30
        self.draw_gesture_icon(frame, computer_x, computer_y, self.computer_gesture, 60)
        cv2.putText(frame, "CPU", (computer_x + 15, computer_y + 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["red"], 2)
    
    def draw_result_state(self, frame, center_x, center_y):
        """Draw clean result state"""
        # Result box
        box_width = 300
        box_height = 100
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2
        
        # Determine result styling
        if self.round_winner == "player":
            result_text = "YOU WIN!"
            bg_color = self.colors["navy"]
            text_color = self.colors["lime"]
        elif self.round_winner == "computer":
            result_text = "COMPUTER WINS!"
            bg_color = self.colors["maroon"]
            text_color = self.colors["red"]
        else:
            result_text = "IT'S A TIE!"
            bg_color = self.colors["teal"]
            text_color = self.colors["gold"]
        
        # Clean background
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     bg_color, -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     text_color, 3)
        
        # Result text
        cv2.putText(frame, result_text, (box_x + 30, box_y + 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.4, text_color, 3)
    
    def draw_countdown_state(self, frame, center_x, center_y):
        """Draw clean countdown state"""
        # Countdown box
        box_width = 300
        box_height = 80
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2
        
        # Clean background
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["blue"], -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["white"], 2)
        
        # Countdown text
        countdown_text = f"Next round in: {int(self.countdown_timer)}"
        cv2.putText(frame, countdown_text, (box_x + 30, box_y + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.colors["white"], 2)
    
    def draw_game_winner(self, frame, center_x, center_y, winner):
        """Draw clean game winner announcement"""
        # Winner box
        box_width = 450
        box_height = 120
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2
        
        # Clean background
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["gold"], -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     self.colors["black"], 3)
        
        # Winner text
        winner_text = f"{winner.upper()} WINS THE GAME!"
        winner_color = self.colors["lime"] if winner == "player" else self.colors["red"]
        
        cv2.putText(frame, winner_text, (box_x + 30, box_y + 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, winner_color, 3)
        
        # Play again instruction
        cv2.putText(frame, "Press 'r' to play again!", (box_x + 80, box_y + 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["black"], 2)
    
    def draw_clean_instructions(self, frame, width, height):
        """Draw clean instructions at the bottom"""
        # Instructions bar
        bar_height = 50
        bar_y = height - bar_height
        
        # Clean background
        cv2.rectangle(frame, (0, bar_y), (width, height), self.colors["navy"], -1)
        cv2.rectangle(frame, (0, bar_y), (width, height), self.colors["white"], 2)
        
        # Instructions text (centered and complete)
        instructions_text = "Press 'q' to quit, 'r' to reset, 'b' for best of 5, 'h' for help"
        
        # Calculate text size to ensure it fits
        font_scale = 0.6
        thickness = 2
        
        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(instructions_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        # If text is too wide, reduce font size
        while text_width > width - 40 and font_scale > 0.3:
            font_scale -= 0.1
            (text_width, text_height), _ = cv2.getTextSize(instructions_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        # Center the text
        text_x = (width - text_width) // 2
        text_y = bar_y + (bar_height + text_height) // 2
        
        cv2.putText(frame, instructions_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, self.colors["white"], thickness)
    
    def draw_progress_bar(self, frame, width, height):
        """Draw clean progress bar for best of 5 mode"""
        bar_width = 200
        bar_height = 12
        bar_x = width - bar_width - 20
        bar_y = 320
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     self.colors["black"], -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     self.colors["white"], 1)
        
        # Progress calculation
        total_games = self.games_to_win
        current_progress = max(self.player_score, self.computer_score)
        progress_ratio = current_progress / total_games
        
        # Filled progress
        fill_width = int(bar_width * progress_ratio)
        progress_color = self.colors["lime"] if self.player_score > self.computer_score else self.colors["red"]
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                     progress_color, -1)
        
        # Progress text
        progress_text = f"Best of 5: {current_progress}/{total_games}"
        cv2.putText(frame, progress_text, (bar_x, bar_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors["white"], 1)
    
    def draw_help_overlay(self, frame):
        """Draw a help overlay with game instructions"""
        height, width = frame.shape[:2]
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), self.colors["black"], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Help content
        help_width = 600
        help_height = 500
        help_x = (width - help_width) // 2
        help_y = (height - help_height) // 2
        
        # Help box
        cv2.rectangle(frame, (help_x, help_y), (help_x + help_width, help_y + help_height), 
                     self.colors["navy"], -1)
        cv2.rectangle(frame, (help_x, help_y), (help_x + help_width, help_y + help_height), 
                     self.colors["gold"], 3)
        
        # Title
        cv2.putText(frame, "GAME HELP", (help_x + 200, help_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.colors["gold"], 3)
        
        # Help content
        help_lines = [
            "GESTURES:",
            "• Rock: Make a fist (all fingers closed)",
            "• Paper: Open palm (all fingers extended)",
            "• Scissors: Peace sign (index + middle only)",
            "",
            "CONTROLS:",
            "• 'q' - Quit the game",
            "• 'r' - Reset scores",
            "• 'b' - Toggle best of 5 mode",
            "• 'h' - Show/hide this help",
            "",
            "TIPS:",
            "• Ensure good lighting",
            "• Keep hand steady",
            "• Position hand clearly in camera",
            "• Wait for gesture detection"
        ]
        
        y_offset = help_y + 80
        for line in help_lines:
            if line.startswith("•"):
                color = self.colors["lime"]
                font_scale = 0.6
            elif line.endswith(":"):
                color = self.colors["gold"]
                font_scale = 0.8
            else:
                color = self.colors["white"]
                font_scale = 0.6
            
            cv2.putText(frame, line, (help_x + 20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)
            y_offset += 30
        
        # Close instruction
        cv2.putText(frame, "Press 'h' again to close", (help_x + 180, help_y + 450), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["cyan"], 2)
    
    def draw_progress_bar(self, frame):
        """Draw a progress bar showing game progress"""
        height, width = frame.shape[:2]
        
        # Progress bar for best of 5 mode
        if self.best_of_5_mode:
            bar_width = 300
            bar_height = 15
            bar_x = width - bar_width - 20
            bar_y = 20
            
            # Background bar
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         self.colors["black"], -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         self.colors["white"], 2)
            
            # Progress calculation
            total_games = self.games_to_win
            current_progress = max(self.player_score, self.computer_score)
            progress_ratio = current_progress / total_games
            
            # Filled progress
            fill_width = int(bar_width * progress_ratio)
            progress_color = self.colors["lime"] if self.player_score > self.computer_score else self.colors["red"]
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                         progress_color, -1)
            
            # Progress text
            progress_text = f"Best of 5: {current_progress}/{total_games}"
            cv2.putText(frame, progress_text, (bar_x, bar_y + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["white"], 2)
    
    
    
    def run_game(self):
        """Enhanced main game loop"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("🎮 Enhanced Rock Paper Scissors Game Started! 🎮")
        print("✨ Show your hand gesture to play! ✨")
        print("🎯 Controls:")
        print("  'q' - Quit game")
        print("  'r' - Reset scores")
        print("  'b' - Toggle best of 5 mode")
        print("  'h' - Show/hide help")
        
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
                    gesture, confidence = self.get_gesture(hand_landmarks)
                    
                    if gesture and confidence > 0.7 and (current_time - self.last_gesture_time) > self.gesture_cooldown:
                        self.player_gesture = gesture
                        self.computer_gesture = random.choice(self.gestures)
                        self.round_winner = self.determine_winner(self.player_gesture, self.computer_gesture)
                        self.update_scores(self.round_winner)
                        self.round_count += 1
                        self.game_state = "result"
                        self.last_gesture_time = current_time
                        self.gesture_confidence = confidence
                        
                        # Update gesture history
                        self.update_gesture_history(gesture)
                        
                        print(f"🎲 Round {self.round_count}: You played {gesture}, Computer played {self.computer_gesture}")
                        print(f"🏆 Result: {self.round_winner}")
                        
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
                    self.gesture_confidence = 0
            
            # Draw UI
            hand_landmarks = results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None
            self.draw_ui(frame, hand_landmarks)
            
            # Display frame
            cv2.imshow('🎮 Enhanced Rock Paper Scissors Game 🎮', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_game()
            elif key == ord('b'):
                self.toggle_best_of_5()
            elif key == ord('h'):
                self.show_help = not self.show_help
                if self.show_help:
                    self.help_timer = current_time
        
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
        self.gesture_confidence = 0
        self.gesture_history.clear()
        

        
        print("🔄 Game reset!")
    
    def toggle_best_of_5(self):
        """Toggle between regular mode and best of 5 mode"""
        self.best_of_5_mode = not self.best_of_5_mode
        mode_text = "Best of 5" if self.best_of_5_mode else "Regular"
        print(f"🎯 Switched to {mode_text} mode!")
        self.reset_game()

if __name__ == "__main__":
    game = EnhancedRockPaperScissorsGame()
    try:
        game.run_game()
    except KeyboardInterrupt:
        print("\n🎮 Game interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🎮 Game ended!")
