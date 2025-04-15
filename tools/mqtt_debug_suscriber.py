import paho.mqtt.client as mqtt
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/mqtt_subscriber.log"),
        logging.StreamHandler()
    ]
)

# Configuración MQTT
TOPIC = "rpi/ai/results/pedro"
BROKER = "broker.hivemq.com"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker at {BROKER}:{PORT}")
    client.subscribe(TOPIC)
    logging.info(f"Subscribed to topic: {TOPIC}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logging.info(f"Message received on topic '{msg.topic}': {payload}")

# Cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

logging.info("Connecting to MQTT broker...")
client.connect(BROKER, PORT)
client.loop_forever()