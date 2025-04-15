import numpy as np
import cv2
import logging
import random
from config import Config

class SensorInput:
    """
    Handles sensor input abstraction for the system, including camera and temperature.
    Allows switching between real hardware and simulated values.
    """

    def __init__(self, config_path="config/settings.yaml"):
        # Load settings from configuration file
        self.cfg = Config(config_path)

        # Camera-related settings
        self.camera_enabled = self.cfg.get("sensors", "camera_enabled", default=True)
        self.camera_index = self.cfg.get("sensors", "camera_index", default=0)
        self.input_shape = self.cfg.get("model", "input_shape", default=[1, 224, 224, 3])

        # Temperature sensor settings
        self.temperature_enabled = self.cfg.get("sensors", "temperature_enabled", default=False)
        self.temperature_simulated = self.cfg.get("sensors", "temperature_simulated", default=True)

        # Initialize camera if enabled
        if self.camera_enabled:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logging.warning(f"Camera index {self.camera_index} could not be opened. Falling back to dummy image.")
                self.camera_enabled = False
        else:
            self.cap = None

    def get_input(self):
        """
        Collects all active sensor inputs and returns them as a dictionary.
        Keys: "image", "temperature"
        """
        result = {}

        # Capture image from camera or generate dummy input
        if self.camera_enabled and self.cap:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logging.warning("Unable to read frame from camera. Using dummy image.")
                img = self._dummy_input()
            else:
                try:
                    # Resize and convert frame to RGB
                    img = cv2.resize(frame, (self.input_shape[2], self.input_shape[1]))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = img.reshape(self.input_shape).astype(np.uint8)
                except Exception as e:
                    logging.warning(f"Error processing camera frame: {e}. Using dummy image.")
                    img = self._dummy_input()
        else:
            logging.warning("Camera not enabled or unavailable. Using dummy image.")
            img = self._dummy_input()

        result["image"] = img

        # Read or simulate temperature if enabled
        if self.temperature_enabled:
            if self.temperature_simulated:
                temp = self._simulate_temperature()
            else:
                temp = self._read_real_temperature()  # Placeholder for hardware integration
            result["temperature"] = temp

        return result

    def _dummy_input(self):
        """
        Generates a dummy image with random noise (used when camera is not available).
        """
        return (np.random.rand(*self.input_shape) * 255).astype(np.uint8)

    def _simulate_temperature(self):
        """
        Returns a simulated temperature value between 18.0°C and 30.0°C.
        """
        temp = round(random.uniform(18.0, 30.0), 2)
        logging.debug(f"Simulated temperature: {temp} °C")
        return temp

    def _read_real_temperature(self):
        """
        Stub function for real temperature sensor input (GPIO, I2C, etc.).
        """
        raise NotImplementedError("Reading physical temperature sensor not yet implemented.")

    def release(self):
        """
        Releases the camera resource properly.
        """
        if self.cap:
            self.cap.release()

# Quick standalone test
if __name__ == "__main__":
    sensor = SensorInput()
    for _ in range(5):
        data = sensor.get_input()
        print(f"Image shape: {data['image'].shape}")
        if "temperature" in data:
            print(f"Temperature: {data['temperature']} °C")
    sensor.release()