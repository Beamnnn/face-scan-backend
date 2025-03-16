import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import face_recognition
from database import save_scan_result, get_all_scans
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

app = FastAPI()
# สร้างโฟลเดอร์เก็บรูป
IMAGE_FOLDER = "face_data"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# เชื่อมต่อ MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("mongodb+srv://admin:1234@cluster0.pbv9t.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

client = MongoClient(MONGO_URI)
db = client["face_recognition"]
collection = db["registered_faces"]

# อนุญาตให้ Frontend ใช้งาน API ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Face Recognition API is running!"}

@app.post("/register-face/")
async def register_face(name: str = Form(...), file: UploadFile = File(...)):
    """ บันทึกใบหน้าพร้อมชื่อของผู้ใช้ใหม่ """
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # ตรวจจับใบหน้า
    face_encodings = face_recognition.face_encodings(img)

    if len(face_encodings) == 0:
        raise HTTPException(status_code=400, detail="No face detected")

    # เก็บข้อมูลใบหน้าลงในฐานข้อมูล
    face_data = {
        "name": name,
        "encoding": face_encodings[0].tolist()
    }
    collection.insert_one(face_data)

    img_path = f"{IMAGE_FOLDER}/{name}.jpg"
    with open(img_path, "wb") as f:
        f.write(contents)

    return {"message": f"Face registered for {name}", "file_saved": img_path}

@app.post("/scan-face/")
async def scan_face(file: UploadFile = File(...)):
    """ ตรวจจับใบหน้าและระบุว่าเป็นใคร """
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # ตรวจจับใบหน้า
    face_encodings = face_recognition.face_encodings(img)

    if len(face_encodings) == 0:
        return {"message": "No face detected"}

    input_encoding = face_encodings[0]
    best_match = None
    best_distance = float("inf")
    threshold = 0.5  # Confidence threshold for matching

    for record in collection.find():
        db_encoding = np.array(record["encoding"])
        distance = face_recognition.face_distance([db_encoding], input_encoding)[0]
        if distance < best_distance and distance < threshold:
            best_distance = distance
            best_match = record["name"]

    if best_match:
        return {"message": f"Recognized: {best_match}"}
    else:
        return {"message": "Face not recognized"}

@app.get("/scan-history/")
def scan_history():
    try:
        history = get_all_scans()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)