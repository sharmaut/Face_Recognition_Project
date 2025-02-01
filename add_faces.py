import face_recognition
from pymongo import MongoClient
import certifi

# MongoDB connection
CONNECTION_STRING = "mongodb+srv://new-user:01Apfn4y8Od411zw@facerecognitioncluster.sr827xe.mongodb.net/?retryWrites=true&w=majority&appName=facerecognitioncluster"

# Connect to MongoDB Atlas
try:
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
    print("Connected to MongoDB Atlas successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")
    exit()

db = client['face_recognition_db']
collection = db['known_faces']

# Function to add known faces
def add_face(image_path, name, context):
    try:
        # Load image and encode face
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            face_encoding = encodings[0]  # Use the first detected face
            # Create a dictionary for MongoDB
            face_data = {
                "name": name,
                "context": context,
                "encoding": face_encoding.tolist()  # Convert NumPy array to list
            }
            # Insert data into MongoDB
            collection.insert_one(face_data)
            print(f"Face data for {name} added successfully.")
        else:
            print("No face detected in the provided image.")

    except Exception as e:
        print(f"Error adding face: {e}")

# Example: Add a face
add_face("/Users/utsavsharma/Documents/Face Recognition Project/Sample.png", "Utsav", "Sample user")
