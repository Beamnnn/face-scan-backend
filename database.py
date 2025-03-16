from pymongo import MongoClient
import os
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:1234@cluster0.pbv9t.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "face_recognition")  # <-- เพิ่มบรรทัดนี้
client = MongoClient(MONGO_URI)

print(client.list_database_names())  # ถ้ารันได้แสดงว่าเชื่อมต่อสำเร็จ

db = client[DB_NAME]
face_collection = db["face_records"]

def save_scan_result(name: str, faces_detected: int):
    record = {"name": name, "faces_detected": faces_detected}
    face_collection.insert_one(record)
    return record

def get_all_scans():
    return list(face_collection.find({}, {"_id": 0}))
