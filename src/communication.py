import json
import logging
import requests
import numpy as np
import paho.mqtt.client as mqtt
from config import Config

class Communicator:
    """
    Manages outgoing communication via MQTT and/or REST based on configuration.
    Sends inference results and additional sensor data to configured endpoints.
    """

    def __init__(self, config_path="config/settings.yaml"):
        self.cfg = Config(config_path)

        # MQTT setup
        mqtt_cfg = self.cfg.get("communication", "mqtt", default={})
        self.mqtt_enabled = mqtt_cfg.get("enabled", False)
        self.mqtt_topic = mqtt_cfg.get("topic", "rpi/ai/results")
        self.mqtt_client = None

        if self.mqtt_enabled:
            try:
                self.mqtt_client = mqtt.Client()
                self.mqtt_client.connect(mqtt_cfg["broker"], mqtt_cfg["port"])
                self.mqtt_client.loop_start()
                logging.info(f"MQTT connected to {mqtt_cfg['broker']}:{mqtt_cfg['port']}")
            except Exception as e:
                logging.error(f"Failed to connect to MQTT broker: {e}")
                self.mqtt_enabled = False

        # REST setup
        rest_cfg = self.cfg.get("communication", "rest", default={})
        self.rest_enabled = rest_cfg.get("enabled", False)
        self.rest_endpoint = rest_cfg.get("endpoint", "")

    def publish_result(self, data: dict):
        """
        Publishes a data dictionary containing inference result and sensor readings.
        Example: {"result": np.array([...]), "temperature": 23.5}

        Parameters:
            data (dict): Inference and sensor data
        """
        # Prepare payload for publishing
        try:
            payload = {}
            for key, value in data.items():
                if isinstance(value, np.ndarray):
                    payload[key] = value.tolist()
                else:
                    payload[key] = value
        except Exception as e:
            logging.error(f"Failed to serialize payload: {e}")
            return

        # Send via MQTT
        if self.mqtt_enabled and self.mqtt_client:
            try:
                self.mqtt_client.publish(self.mqtt_topic, json.dumps(payload))
                logging.debug(f"MQTT published to {self.mqtt_topic}: {payload}")
            except Exception as e:
                logging.error(f"MQTT publish failed: {e}")

        # Send via REST
        if self.rest_enabled and self.rest_endpoint:
            try:
                response = requests.post(self.rest_endpoint, json=payload, timeout=2)
                logging.info(f"REST POST to {self.rest_endpoint} [status {response.status_code}]")
            except Exception as e:
                logging.error(f"REST POST failed: {e}")

    def stop(self):
        """
        Cleanly disconnects from MQTT if active.
        """
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()