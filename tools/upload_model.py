import requests
import os

# Target REST endpoint
UPLOAD_URL = "http://localhost:5000/api/model/upload"
MODEL_PATH = "models/model.tflite"  # Default model path to upload

def upload_model(filepath):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"Uploading model: {filepath} → {UPLOAD_URL}")
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'application/octet-stream')}
            response = requests.post(UPLOAD_URL, files=files)

        print(f"Response {response.status_code}: {response.json()}")

    except Exception as e:
        print(f"Failed to upload model: {e}")


if __name__ == "__main__":
    upload_model(MODEL_PATH)