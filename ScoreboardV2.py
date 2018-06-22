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
  
    def __init__(self,host,port,keepalive_interval,topic)
        self.connect(host,port,keepalive_interval)
        self.loop_start()
 
  
    def on_connect(self,mosq, obj, rc):
        print("Connected to broker")
        
        
    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed to topic: " + str(mid) + " with QoS: " + str(granted_qos))
        
        
    def on_message(self,mosq,obj, msg):
        print ("Received: " + msg.payload)
        message_handler(msg)
        
        
    def message_handler(msg):
        message_verb, message_value = msg.split(';')
        if message_verb == "homescore"
            homescore(message_value)
          
          
        #TODO ADD MORE IF BRANCHES
        
    def homescore(score):
        homescorewidget.value = score
        
    
class ScoreboardDisplay:
  
    def __init__(self):
        
        options = RGBMAtrixOptions()
        #TODO MOVE TO CONFIG FILE
        options.hardware_mapping = "adafruit-hat"
        options.disable_hardware_pulsing = True
        options.rows = 16
        options.columns = 32
        options.chain_length = 4
        options.multiplexing = 8 #CORRECT value for 1/4 SCAN PANELS
        
        self.matrix = RGBMatrix(options = options)
      
class DisplayWidget()

    def __init__(self,x,y,xwidth,ywidth,is_visible = True):
        self.x = x
        self.y = y
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.is_visible = is_visible
        self.value = 0
        
    def drawtext(text,x,y,colour,font):
        length = graphic.DrawText(self.offscreen_canvas,self.font,self.x + x,self.y + y, self.colour, text)
        
    def showimage(image,x,y):
        self.offscreen_canvas.SetImage(image,self.x + x,self.y + y)
        
    def fillwidget(colour):
        t = datetime.datetime.now()
        ms = t.microsecond
        if ms % 1000 > 500:
            c=255
        else:
            c=0
        for i in range(self.x,self.x + self.xwidth - 1):
            for j in range(self.y,self.y + self.ywidth - 1):
                self.offscreen_canvas.SetPixel(i,j,colour,colour,colour)
        
        
    def displayscore():
        digits = {'0','number0r.png',
                 }
        scoreimage = Image.open(digits[self.value])
        self.showimage(scoreimage,0,0)
        
    def displayclock()
        t = datetime.datetime.now()
        clocktext = t.strftime('%H:%M:%S')
        self.showtext(clocktext,0,0)
        
    def displaytimer()
        t = self.value
        if t.hour == 0:
            timertext = t.strftine('%M:%S')
        else:
            timertext = t.strftime('%H:%M:%S')
        self.showext(timertext,0,0)
        
    def displaymessage():
        self.showtext(self.value,0,0)
        
    def displayheartbeat():
      # FLASH ALL PIXELS ONTHE WIDGET
      t=datetime.datetime.now()
      ms = t.micrsecond
      if ms % 1000 > 500:
          c=255
      else:
          c=0
          
      self.fillwidget(c)
      
      
    
        


# main function
if __name__ == "__main__":
  #initialise MQTT broker
  
  #initialise MQTT client
  mqttclient = MyMQTTClient(config.host, config.port, config.keepalive_interval,conf.topic)
  
  #initialise Matrix display
  sb_display = MatrixDisplay()
  
  #initialise screen widgets
  homescorewidget = DisplayWidget(16,16,16,32)
  awayscorewidget = DisplayWidget(0,16,16,32)
  clockwidget = DisplayWidget(0,0,64,16)
  timerwidget = DisplayWidget(0,0,64,16)
  messagewidget = DisplayWidget(0,0,64,16)
  heartbeatwidget = DisplayWidget(0,0,1,1)
  
  
  #loop
  
  sb_display.offscreen_canvas.clear()
  #clear the display
  
  #set active widgets 
  homescorewidget.displayscore()
  awayscorewidget.displayscore()
  clockwidget.displayclock()
  timerwidget.displaytimer()
  heartbeatwidget.displayheartbeat()
  
  
  #wait a short time
  time.sleep(0.05)
  
  #refresh the display
  sb_display.SwapOnVSync(sb_display.offscreen_canvas)
  
  #repeat