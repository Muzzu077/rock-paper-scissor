# Real-Time Rock-Paper-Scissors Game with Hand Gesture Recognition

A computer vision system that detects hand gestures in real-time and plays Rock-Paper-Scissors against a computer opponent.

## Features

- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand landmark detection
- **Gesture Recognition**: Automatically detects rock, paper, and scissors gestures
- **Computer Opponent**: Randomly generates moves for continuous gameplay
- **Scoring System**: Tracks player vs. computer scores
- **Visual Feedback**: Shows game state, moves, and results in real-time
- **Auto-reset**: Automatically prepares for the next round after a countdown

## Gesture Definitions

- **Rock**: All fingers closed (fist)
- **Paper**: All fingers extended (open palm)
- **Scissors**: Only index and middle finger extended (peace sign)

## Requirements

- Python 3.7+
- Webcam
- Good lighting for hand detection

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the game:
   ```bash
   python rock_paper_scissors_game.py
   ```

2. Position your hand in front of the webcam
3. Show one of the three gestures:
   - **Rock**: Make a fist
   - **Paper**: Open your palm with all fingers extended
   - **Scissors**: Show peace sign (index and middle finger only)

4. The game will automatically detect your gesture and play against the computer
5. Watch the results and scores update in real-time

## Controls

- **'q'**: Quit the game
- **'r'**: Reset scores and start over

## Game Flow

1. **Waiting State**: Show your hand gesture
2. **Detection**: Game recognizes your move and generates computer's move
3. **Result**: Winner is determined and displayed
4. **Countdown**: 3-second countdown before next round
5. **Repeat**: Game automatically returns to waiting state

## Technical Details

- **Hand Detection**: MediaPipe Hands with 21 landmark points
- **Gesture Classification**: Based on finger tip vs. joint positions
- **Frame Processing**: OpenCV for video capture and display
- **Game Logic**: State machine for smooth gameplay transitions

## Troubleshooting

- **No hand detected**: Ensure good lighting and hand is clearly visible
- **Gesture not recognized**: Try adjusting hand position and ensure fingers are clearly extended/closed
- **Webcam issues**: Check if webcam is accessible and not used by other applications

## Future Enhancements

- Sound effects for wins/losses
- Best-of-5 mode with final winner announcement
- Animated countdown and visual effects
- Multiple hand support for two-player mode
- Gesture training mode for improved accuracy

## License

This project is open source and available under the MIT License.
