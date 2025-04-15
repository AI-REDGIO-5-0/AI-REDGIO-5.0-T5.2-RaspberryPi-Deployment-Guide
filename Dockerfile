# Dockerfile for edge_node
FROM python:3.10-slim

WORKDIR /app

# Install system packages for OpenCV, image support, etc.
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run main app
CMD ["python", "src/main.py"]