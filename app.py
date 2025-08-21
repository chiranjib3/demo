from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import mediapipe as mp
import numpy as np
import base64
import io
from PIL import Image
import threading
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

# Global variables for AI processing
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Store active rooms and users
active_rooms = {}
user_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<room_id>')
def room(room_id):
    return render_template('room.html', room_id=room_id)

@socketio.on('connect')
def on_connect():
    print(f'Client connected: {request.sid}')
    user_sessions[request.sid] = {
        'room': None,
        'username': None,
        'ai_features': {
            'face_detection': False,
            'hand_tracking': False,
            'pose_detection': False
        }
    }

@socketio.on('disconnect')
def on_disconnect():
    print(f'Client disconnected: {request.sid}')
    if request.sid in user_sessions:
        room = user_sessions[request.sid]['room']
        if room and room in active_rooms:
            active_rooms[room].discard(request.sid)
            if not active_rooms[room]:
                del active_rooms[room]
        del user_sessions[request.sid]

@socketio.on('join_room')
def on_join_room(data):
    room_id = data['room']
    username = data['username']
    
    join_room(room_id)
    user_sessions[request.sid]['room'] = room_id
    user_sessions[request.sid]['username'] = username
    
    if room_id not in active_rooms:
        active_rooms[room_id] = set()
    active_rooms[room_id].add(request.sid)
    
    emit('user_joined', {
        'username': username,
        'user_id': request.sid,
        'room_users': len(active_rooms[room_id])
    }, room=room_id)

@socketio.on('leave_room')
def on_leave_room(data):
    room_id = data['room']
    leave_room(room_id)
    
    if request.sid in user_sessions:
        username = user_sessions[request.sid]['username']
        user_sessions[request.sid]['room'] = None
        
        if room_id in active_rooms:
            active_rooms[room_id].discard(request.sid)
            emit('user_left', {
                'username': username,
                'user_id': request.sid,
                'room_users': len(active_rooms[room_id])
            }, room=room_id)

@socketio.on('video_frame')
def handle_video_frame(data):
    try:
        # Decode base64 image
        image_data = base64.b64decode(data['frame'].split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Get user's AI preferences
        user_id = request.sid
        ai_features = user_sessions[user_id]['ai_features']
        
        # Apply AI processing based on user preferences
        processed_frame = process_frame_with_ai(frame, ai_features)
        
        # Convert back to base64
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Broadcast to room
        room_id = user_sessions[user_id]['room']
        if room_id:
            emit('video_frame', {
                'frame': f'data:image/jpeg;base64,{processed_b64}',
                'user_id': user_id,
                'username': user_sessions[user_id]['username']
            }, room=room_id, include_self=False)
            
    except Exception as e:
        print(f"Error processing video frame: {e}")

@socketio.on('screen_share_started')
def handle_screen_share_started():
    user_id = request.sid
    if user_id in user_sessions:
        room_id = user_sessions[user_id]['room']
        username = user_sessions[user_id]['username']
        if room_id:
            emit('screen_share_started', {
                'user_id': user_id,
                'username': username
            }, room=room_id, include_self=False)

@socketio.on('screen_share_ended')
def handle_screen_share_ended():
    user_id = request.sid
    if user_id in user_sessions:
        room_id = user_sessions[user_id]['room']
        username = user_sessions[user_id]['username']
        if room_id:
            emit('screen_share_ended', {
                'user_id': user_id,
                'username': username
            }, room=room_id, include_self=False)

@socketio.on('toggle_ai_feature')
def toggle_ai_feature(data):
    feature = data['feature']
    enabled = data['enabled']
    
    if request.sid in user_sessions:
        user_sessions[request.sid]['ai_features'][feature] = enabled
        emit('ai_feature_toggled', {
            'feature': feature,
            'enabled': enabled
        })

@socketio.on('chat_message')
def handle_chat_message(data):
    room_id = user_sessions[request.sid]['room']
    username = user_sessions[request.sid]['username']
    
    if room_id:
        emit('chat_message', {
            'username': username,
            'message': data['message'],
            'timestamp': time.time()
        }, room=room_id)

def process_frame_with_ai(frame, ai_features):
    """Apply AI processing to video frame based on enabled features"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Face Detection
    if ai_features['face_detection']:
        results = face_detection.process(rgb_frame)
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)
    
    # Hand Tracking
    if ai_features['hand_tracking']:
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # Pose Detection
    if ai_features['pose_detection']:
        results = pose.process(rgb_frame)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    return frame

@app.route('/api/rooms')
def get_active_rooms():
    return jsonify({
        'rooms': [
            {
                'id': room_id,
                'users': len(users)
            }
            for room_id, users in active_rooms.items()
        ]
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
