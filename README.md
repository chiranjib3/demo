# AI Video Streaming App

A real-time video streaming application with AI-powered features using free APIs and libraries.

## Features

- **Real-time Video Streaming**: WebSocket-based video streaming between multiple users
- **AI-Powered Analysis**: 
  - Face Detection using MediaPipe
  - Hand Tracking and Gesture Recognition
  - Full Body Pose Detection
- **Interactive Chat**: Real-time messaging in video rooms
- **Room Management**: Create or join existing rooms
- **Modern UI**: Responsive design with Bootstrap and Font Awesome icons

## Technologies Used

- **Backend**: Flask, Flask-SocketIO, Python
- **AI/ML**: MediaPipe, OpenCV, NumPy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Real-time Communication**: Socket.IO, WebSockets

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Home Page**: Enter your username and optionally a room ID
2. **Join Room**: Click "Start Streaming" to join or create a room
3. **Video Controls**: 
   - Toggle video/audio on/off
   - Share screen
   - Leave room
4. **AI Features**: Enable/disable AI features in the control panel:
   - Face Detection
   - Hand Tracking
   - Pose Detection
5. **Chat**: Use the chat panel to communicate with other users

## API Endpoints

- `GET /` - Home page
- `GET /room/<room_id>` - Video room interface
- `GET /api/rooms` - Get list of active rooms
- WebSocket events for real-time communication

## Free APIs and Libraries Used

- **MediaPipe** (Google): Free AI/ML library for face, hand, and pose detection
- **OpenCV**: Open-source computer vision library
- **Socket.IO**: Free real-time communication library
- **Bootstrap**: Free CSS framework
- **Font Awesome**: Free icon library

## Browser Requirements

- Modern browser with WebRTC support
- Camera and microphone permissions
- JavaScript enabled

## Security Notes

- Change the `SECRET_KEY` in `app.py` for production use
- Consider implementing user authentication for production
- Add rate limiting for video frame processing

## Performance Optimization

- Video frames are compressed to JPEG format
- AI processing is optional and can be toggled per user
- WebSocket connections are managed efficiently
- Canvas-based video processing for better performance

## Troubleshooting

- **Camera not working**: Check browser permissions
- **High CPU usage**: Disable AI features if not needed
- **Connection issues**: Ensure port 5000 is available
- **Video quality**: Adjust JPEG quality in the code if needed
