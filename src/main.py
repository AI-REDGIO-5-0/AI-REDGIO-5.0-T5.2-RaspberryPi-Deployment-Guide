import os
from datetime import datetime
import time
import logging
import numpy as np
import cv2
from config import Config
from inference import InferenceEngine
from sensors import SensorInput
from communication import Communicator

def main():
    # Configure logging to both file and console
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "runtime.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

    cfg = Config()

    # Load AI model and configuration
    engine = InferenceEngine()
    input_shape = engine.input_shape
    interval = cfg.get("sensors", "read_interval", default=5)

    # Initialize sensors and communication
    sensor = SensorInput()
    comm = Communicator()

    logging.info(f"Starting inference loop every {interval} seconds...")

    while True:
        # Acquire inputs from all active sensors
        data = sensor.get_input()
        image = data["image"]
        temperature = data.get("temperature")

        # Run inference on the image input
        result = engine.predict(image)
        logging.info(f"Inference result: {result}")

        # Log any additional sensor values (e.g., temperature)
        if temperature is not None:
            logging.info(f"Temperature reading: {temperature} °C")

        # Build payload with all available data
        payload = {
            "result": result,
            "temperature": temperature
        }

        # Publish the result through communication channels (MQTT/REST)
        comm.publish_result(payload)

        # Wait before the next sensor read
        time.sleep(interval)

    # Cleanup: release hardware and communication resources
    sensor.release()
    comm.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()