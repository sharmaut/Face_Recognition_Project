import cv2
import numpy as np
import dlib
from pymongo import MongoClient
import certifi
import subprocess
import time

# MongoDB Connection
CONNECTION_STRING = "mongodb+srv://new-user:01Apfn4y8Od411zw@facerecognitioncluster.sr827xe.mongodb.net/?retryWrites=true&w=majority&appName=facerecognitioncluster"

try:
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
    print("Connected to MongoDB Atlas successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")
    exit()

db = client['face_recognition_db']
collection = db['known_faces']

# Load known faces from MongoDB
def load_known_faces():
    known_faces = []
    known_names = []
    for document in collection.find():
        if 'encoding' in document and isinstance(document['encoding'], list):
            known_faces.append(np.array(document['encoding']))
            known_names.append(document['name'])
        else:
            print(f"Skipping document without valid 'encoding': {document['_id']}")
    return known_faces, known_names

known_face_encodings, known_face_names = load_known_faces()

# Dlib face landmark and recognition models
shape_predictor_path = '//Users/utsavsharma/Documents/Face Recognition Project/shape_predictor_68_face_landmarks.dat'
face_recognition_model_path = '/Users/utsavsharma/Documents/Face Recognition Project/dlib_face_recognition_resnet_model_v1.dat'

try:
    sp = dlib.shape_predictor(shape_predictor_path)
    facerec = dlib.face_recognition_model_v1(face_recognition_model_path)
    print("Dlib models loaded successfully.")
except Exception as e:
    print(f"Error loading Dlib models: {e}")
    exit()

# Lock the screen using macOS commands
def lock_screen():
    subprocess.call('pmset displaysleepnow', shell=True)
    print("Screen locked.")

# Unlock function (placeholder - you can notify or log the unlock event)
def unlock_screen():
    print("Recognized face detected. Unlocking...")

# Manage locking and unlocking
lock_state = False
last_recognized_time = time.time()
LOCK_TIMEOUT = 5  # Seconds to wait before locking the screen if no recognized face is detected

def process_video():
    global lock_state, last_recognized_time
    video_capture = cv2.VideoCapture(0)  # Open webcam
    print("Press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error accessing webcam.")
            break

        # Convert frame from BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face locations using dlib's detector
        face_detector = dlib.get_frontal_face_detector()
        detected_faces = face_detector(rgb_frame, 1)

        print(f"Faces detected: {len(detected_faces)}")

        # Compute face encodings
        face_encodings = []
        for rect in detected_faces:
            try:
                # Get landmarks for the detected face
                landmarks = sp(rgb_frame, rect)

                # Compute face descriptor (encoding) from the image and landmarks
                encoding = np.array(facerec.compute_face_descriptor(rgb_frame, landmarks))
                face_encodings.append((encoding, rect))

            except Exception as e:
                print(f"Error computing face encodings: {e}")

        recognized = False
        for encoding, rect in face_encodings:
            matches = [np.linalg.norm(encoding - known) < 0.6 for known in known_face_encodings]
            print(f"Matches: {matches}")  # Debug: Print match results for each face
            name = "Unknown"

            if any(matches):
                match_index = matches.index(True)
                name = known_face_names[match_index]
                print(f"Matched with: {name}")  # Debug: Print the matched name
                recognized = True
            else:
                print("No match found.")  # Debug: Indicate no match

            # Draw a rectangle around the face and add the name label
            top, right, bottom, left = rect.top(), rect.right(), rect.bottom(), rect.left()
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Lock/Unlock logic
        current_time = time.time()
        if recognized:
            last_recognized_time = current_time
            if lock_state:
                unlock_screen()
                lock_state = False
        else:
            if current_time - last_recognized_time > LOCK_TIMEOUT and not lock_state:
                lock_screen()
                lock_state = True

        # Display the resulting frame
        cv2.imshow("Video", frame)

        # Quit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Run the video processing function
process_video()
