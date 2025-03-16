# ใช้ Python image ที่รองรับ dlib
FROM python:3.10-slim

# ติดตั้ง dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    g++ \
    make \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*


# ตั้งค่าตัวแปร Environment
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# กำหนดโฟลเดอร์ทำงาน
WORKDIR /app

COPY main.py requirements.txt database.py face_data/ /app/

# ติดตั้ง dlib และ dependencies
RUN pip install --no-cache-dir cmake dlib
RUN pip install --no-cache-dir -r requirements.txt

# รัน FastAPI ผ่าน Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]