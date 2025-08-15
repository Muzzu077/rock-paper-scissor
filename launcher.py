#!/usr/bin/env python3
"""
Launcher script for Rock Paper Scissors Game
Choose between different versions and testing tools
"""

import os
import sys
import subprocess

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the game banner"""
    print("=" * 60)
    print("    ROCK PAPER SCISSORS GAME LAUNCHER")
    print("=" * 60)
    print()

def print_menu():
    """Print the main menu"""
    print("Available Options:")
    print("1. Basic Game - Simple rock-paper-scissors with hand gestures")
    print("2. Enhanced Game - Advanced features and better detection")
    print("3. Gesture Tester - Test hand gesture detection")
    print("4. Demo Game - Test game logic without webcam")
    print("5. Install Dependencies - Install required packages")
    print("6. Exit")
    print()

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please check your Python environment.")
    except FileNotFoundError:
        print("requirements.txt not found. Please ensure you're in the correct directory.")
    
    input("\nPress Enter to continue...")

def run_basic_game():
    """Run the basic version of the game"""
    print("Starting Basic Game...")
    try:
        subprocess.run([sys.executable, "rock_paper_scissors_game.py"])
    except FileNotFoundError:
        print("Error: rock_paper_scissors_game.py not found!")
        input("Press Enter to continue...")

def run_enhanced_game():
    """Run the enhanced version of the game"""
    print("Starting Enhanced Game...")
    try:
        subprocess.run([sys.executable, "enhanced_game.py"])
    except FileNotFoundError:
        print("Error: enhanced_game.py not found!")
        input("Press Enter to continue...")

def run_gesture_tester():
    """Run the gesture testing tool"""
    print("Starting Gesture Tester...")
    try:
        subprocess.run([sys.executable, "test_gestures.py"])
    except FileNotFoundError:
        print("Error: test_gestures.py not found!")
        input("Press Enter to continue...")

def run_demo_game():
    """Run the demo game"""
    print("Starting Demo Game...")
    try:
        subprocess.run([sys.executable, "demo.py"])
    except FileNotFoundError:
        print("Error: demo.py not found!")
        input("Press Enter to continue...")

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                run_basic_game()
            elif choice == "2":
                run_enhanced_game()
            elif choice == "3":
                run_gesture_tester()
            elif choice == "4":
                run_demo_game()
            elif choice == "5":
                install_dependencies()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
