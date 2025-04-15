from flask import Flask, request, jsonify
import logging
import os
import json
from datetime import datetime
import csv

# Flask app initialization
app = Flask(__name__)

# Folder to store received data and models
DATA_DIR = "logs/rest_data"
MODEL_PATH = "models/model.tflite"
os.makedirs(DATA_DIR, exist_ok=True)

# Configure logging to file
logging.basicConfig(
    filename="logs/rest_data/rest_receiver.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/api/results", methods=["POST"])
def receive_result():
    """
    REST API endpoint that receives POST requests with AI inference and sensor data.
    Saves each request to a JSON file and appends to a CSV log.
    """
    data = request.json
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Log the received payload
    logging.info(f"Received at {timestamp}: {data}")
    print(f"\n{timestamp} → {data}")

    # Save each request to an individual JSON file
    json_path = os.path.join(DATA_DIR, f"{timestamp.replace(':', '-')}.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    # Append data to a CSV log for analysis
    csv_path = os.path.join(DATA_DIR, "data_log.csv")
    write_header = not os.path.exists(csv_path)

    # Flatten result if it's a list or dict
    result = data.get("result", None)
    if isinstance(result, (list, dict)):
        result = json.dumps(result)

    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "result", "temperature"])
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": timestamp,
            "result": result,
            "temperature": data.get("temperature", None)
        })

    # Return JSON response
    return jsonify({"status": "ok"}), 200

@app.route("/api/battery", methods=["GET"])
def get_battery_level():
    """
    Returns the battery level if available, or a notice if running on direct power.
    """
    battery_path = "/sys/class/power_supply/BAT0/capacity"

    if os.path.exists(battery_path):
        try:
            with open(battery_path, "r") as f:
                level = int(f.read().strip())
            return jsonify({
                "status": "ok",
                "battery_level": level,
                "message": "Battery level retrieved successfully."
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error reading battery level: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "unavailable",
            "battery_level": None,
            "message": "No battery detected. System likely running on external power."
        }), 200

@app.route("/api/model/info", methods=["GET"])
def model_info():
    """
    Returns basic information about the current model file.
    """
    if not os.path.exists(MODEL_PATH):
        return jsonify({
            "status": "error",
            "message": "No model file found."
        }), 404

    info = {
        "filename": os.path.basename(MODEL_PATH),
        "size_bytes": os.path.getsize(MODEL_PATH),
        "last_modified": datetime.fromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat()
    }
    return jsonify({
        "status": "ok",
        "model": info
    }), 200

@app.route("/api/model/upload", methods=["POST"])
def upload_model():
    """
    Uploads a new .tflite model and replaces the existing one.
    """
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in request."}), 400

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.tflite'):
        return jsonify({"status": "error", "message": "Only .tflite files are accepted."}), 400

    try:
        filename = secure_filename(file.filename)
        file.save(MODEL_PATH)
        logging.info(f"Model uploaded and saved as {MODEL_PATH}")
        return jsonify({"status": "ok", "message": "Model uploaded successfully."}), 200
    except Exception as e:
        logging.error(f"Failed to upload model: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("REST Receiver listening at http://localhost:5000/api/results")
    app.run(host="0.0.0.0", port=5000)