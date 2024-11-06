
# Gesture-Based Screen Control

Experience futuristic, gesture-driven screen interactions that bring a new level of immersion to everyday tasks. With intuitive gestures for hovering, clicking, scrolling, and zooming, control your screen as if you're in a sci-fi film!

## Features

### 🌐 Virtual Mouse
- **Hover**: Raise your index finger to move the cursor, enabling a hover effect over items on the screen.
- **Click**: Perform a “bell-tap” gesture using your index finger to simulate a click, precisely selecting items with a natural hand motion.
- **Directional Scrolling**: Move both index and middle fingers together in any of four directions (up, down, left, right) to scroll effortlessly in the chosen direction.

### 🔍 Zoom In/Out
- **Pinch Zoom**: Use your index finger and thumb to zoom in or out. This gesture allows you to focus on specific screen areas or adjust the zoom on images with high precision.

## Requirements

- **Hardware**: A high-resolution camera for accurate gesture tracking.
- **Software**: OpenCV and MediaPipe for detecting gestures, plus any additional dependencies listed.

> Ensure these libraries are installed and up-to-date for optimal functionality.

## Installation

1. Clone this repository:
   ```bash
   git clone 
   ```
2. Navigate to the project folder:
   ```bash
   cd gesture-based-screen-control
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the gesture control system by running the main script:
   ```bash
   python main.py
   ```
2. Follow on-screen instructions to calibrate the gestures.

## Controls and Gestures

| Gesture                       | Action                               |
|-------------------------------|--------------------------------------|
| Index Finger Hover            | Move cursor to hover over items      |
| Bell Tap (Index Finger)       | Click or select items                |
| Index + Middle Finger Movement | Scroll in the direction of movement |
| Pinch (Index + Thumb)         | Zoom in/out on screen or images      |

> **Tip**: Ensure good lighting and a clutter-free background for smooth gesture detection.

## Troubleshooting

If gestures aren’t detected accurately:
1. Adjust lighting and camera position for clearer hand visibility.
2. Recalibrate the system if sensitivity needs adjusting.

## Contributing

Contributions to enhance functionality, gestures, and responsiveness are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
