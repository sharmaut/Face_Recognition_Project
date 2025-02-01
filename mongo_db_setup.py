from pymongo import MongoClient
import pymongo
import certifi

# Replace with your actual connection string from MongoDB Atlas
CONNECTION_STRING = "mongodb+srv://new-user:01Apfn4y8Od411zw@facerecognitioncluster.sr827xe.mongodb.net/?retryWrites=true&w=majority&appName=facerecognitioncluster"

# Connect to MongoDB using certifi
client = pymongo.MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

# Check connection
db = client['face_recognition_db']
collection = db['known_faces']
print("Connected to MongoDB Atlas successfully.")

# Check and initialize collection
if collection.count_documents({}) == 0:
    print("Collection is empty. Ready to add data.")
else:
    print("Collection already has data.")

# Insert sample data if the collection is empty
if collection.count_documents({}) == 0:
    sample_data = [
        {
            "name": "Jane Smith",
            "azure_face_id": "5678abcd-1234-ijkl-9101-mnopqrstu",
            "context": "Jane is a graphic designer passionate about painting.",
            "consent": True
        },
        {
            "name": "Unknown User",
            "azure_face_id": "9101abcd-5678-mnop-1234-qrstuvwx",
            "context": "No additional information available.",
            "consent": False
        }
    ]
    collection.insert_many(sample_data)
    print("Sample data inserted into the collection.")

# Verify the data by fetching all records
print("\nRecords in the 'known_faces' collection:")
for record in collection.find():
    print(record)
