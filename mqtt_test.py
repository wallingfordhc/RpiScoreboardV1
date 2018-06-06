import paho.mqtt.client as mqtt
# Define Variables
MQTT_HOST = "192.168.1.103"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "raspi/1"


def on_connect(self, mosq, obj, rc):
    print("connecting")
    mqttc.subscribe(MQTT_TOPIC, 0)
    print("Connect on " + MQTT_HOST)