FROM pytorch/pytorch:2.9.1-cuda13.0-cudnn9-devel
# FROM python:3.13

WORKDIR /app

# Install system dependencies for image processing (OpenCV/Docling)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
