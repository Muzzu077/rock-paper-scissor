#!/usr/bin/env python3
"""
Demo script for Rock Paper Scissors Game
Tests basic functionality without webcam
"""

import random
import time

class DemoGame:
    def __init__(self):
        self.player_score = 0
        self.computer_score = 0
        self.round_count = 0
        self.gestures = ["rock", "paper", "scissors"]
    
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
    
    def play_round(self, player_gesture):
        """Play a single round"""
        computer_gesture = random.choice(self.gestures)
        winner = self.determine_winner(player_gesture, computer_gesture)
        self.update_scores(winner)
        self.round_count += 1
        
        print(f"\n--- Round {self.round_count} ---")
        print(f"You played: {player_gesture.upper()}")
        print(f"Computer played: {computer_gesture.upper()}")
        
        if winner == "player":
            print("🎉 YOU WIN! 🎉")
        elif winner == "computer":
            print("😞 Computer wins...")
        else:
            print("🤝 It's a tie!")
        
        print(f"Score - You: {self.player_score}, Computer: {self.computer_score}")
    
    def run_demo(self):
        """Run the demo game"""
        print("🎮 ROCK PAPER SCISSORS DEMO 🎮")
        print("=" * 40)
        print("This demo simulates the game logic without webcam access.")
        print("You can choose your moves manually to test the game.")
        print()
        
        while True:
            print("\nAvailable moves:")
            for i, gesture in enumerate(self.gestures, 1):
                print(f"{i}. {gesture.upper()}")
            print("4. Quit")
            
            try:
                choice = input("\nChoose your move (1-4): ").strip()
                
                if choice == "4":
                    break
                elif choice in ["1", "2", "3"]:
                    player_gesture = self.gestures[int(choice) - 1]
                    self.play_round(player_gesture)
                    
                    # Simulate countdown
                    print("\nPreparing for next round...")
                    for i in range(3, 0, -1):
                        print(f"Next round in {i}...")
                        time.sleep(1)
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
                    
            except KeyboardInterrupt:
                print("\n\nGame interrupted!")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        # Final results
        print("\n" + "=" * 40)
        print("🎯 FINAL RESULTS 🎯")
        print(f"Total Rounds: {self.round_count}")
        print(f"Your Score: {self.player_score}")
        print(f"Computer Score: {self.computer_score}")
        
        if self.player_score > self.computer_score:
            print("🏆 YOU WIN THE GAME! 🏆")
        elif self.computer_score > self.player_score:
            print("😞 Computer wins the game...")
        else:
            print("🤝 It's a tie game!")
        
        print("\nThanks for playing! 🎮")

if __name__ == "__main__":
    demo = DemoGame()
    try:
        demo.run_demo()
    except Exception as e:
        print(f"Demo error: {e}")
