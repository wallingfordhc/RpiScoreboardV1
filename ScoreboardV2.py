#!/usr/bin/env python
#
# Scoreboard created originally for Wallingford Hockey Club - June 2018
#
# v.0.2
# author d.shannon
# 
import paho.mqtt.client as mqtt
from rgbmatrix import RGBMatrix, RGBMAtrixOptions
from rgbmatrix import graphics
from PIL import image
import time
import datetime
import argparse
import sys

import config

class MyMQTTClient(mqtt.Client):
  
    def on_connect(self,mosq, obj, rc):
        print("Connected to broker")
        
    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed to topic: " + str(mid) + " with QoS: " + str(granted_qos))
      
      


# main function
if __name__ == "__main__":
  #initialise MQTT broker
  
  #initialise MQTT client
  mqttclient = mqtt.Client()
  
  #initialise Matrix display
  sb_display = MatrixDisplay()
  
  #initialise screen widgets
  
  #loop
  
  #clear the display
  
  #draw active widgets 
  
  #repeat