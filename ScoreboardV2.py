#!/usr/bin/env python
#
# Scoreboard created originally for Wallingford Hockey Club - June 2018
#
# v.0.2
# author d.shannon
# 
import paho.mqtt.client as mqtt
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
from PIL import Image
import time
from datetime import datetime
from dateutil import parser

import config


class MyMQTTClient(mqtt.Client):

    def start_connection(self, host, port, keepalive_interval, topic):
        print("trying to connect")
        self.connect(host, 1883, 45)
        self.subscribe(topic, 0)
        self.loop_start()

    def on_connect(self, mosq, obj, flags, rc):
        print("Connected to broker")

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed to topic: " + str(mid) + " with QoS: " + str(granted_qos))

    def on_message(self, mosq, obj, msg):
        print("Received: " + msg.payload)
        self.message_handler(msg)

    def message_handler(self, msg):
        message_verb, message_value = msg.split(';')
        if message_verb == "homescore":
            self.homescore(message_value)

        # TODO ADD MORE IF BRANCHES

    def homescore(self, score):
        homescorewidget.content = score


class ScoreboardDisplay:

    def __init__(self):
        options = RGBMatrixOptions()
        # TODO MOVE TO CONFIG FILE
        options.hardware_mapping = "adafruit-hat"
        options.disable_hardware_pulsing = True
        options.rows = 16
        options.cols = 32
        options.chain_length = 4
        options.multiplexing = 8  # CORRECT value for 1/4 SCAN PANELS

        self.matrix = RGBMatrix(options=options)
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

class DisplayWidget:

    def __init__(self, parentdisplay, x, y, xwidth, ywidth, content="0", is_visible=True):
        self.x = x
        self.y = y
        self.xwidth = xwidth
        self.ywidth = ywidth
        self.is_visible = is_visible
        self.content = content
        self.parentdisplay = parentdisplay

    def showtext(self, text, x, y, font, displaycolour):
        displayfont = graphics.Font()
        displayfont.LoadFont("/home/pi/fonts/" + font)
        length = graphics.DrawText(self.parentdisplay.offscreen_canvas,
                                   displayfont,
                                   self.x + x, self.y + y,
                                   displaycolour, text)

    def showimage(self, image, x, y):
        print("entering showimage")
        self.parentdisplay.offscreen_canvas.SetImage(image, self.x + x, self.y + y)

    def fillwidget(self, colour):
        for i in range(self.x, self.x + self.xwidth - 1):
            for j in range(self.y, self.y + self.ywidth - 1):
                self.parentdisplay.offscreen_canvas.SetPixel(i, j, colour, colour, colour)

    def displayscore(self):
        print("entering displayscore")

        digits = {'0': "number0r.png",
                  '1': "number1r.png",
                  '2': "number2r.png",
                  '3': "number3r.png",
                  '4': "number4r.png",
                  '5': "number5r.png",
                  '6': "number6r.png",
                  '7': "number7r.png",
                  '8': "number8r.png",
                  '9': "number9r.png",
                  '10': "number10r.png",
                  '11': "number11r.png"
                  }

        scoreimage = Image.open(digits[self.content])
        self.showimage(scoreimage, 0, 0)

    def displayclock(self):
        t = datetime.now()
        clocktext = t.strftime('%H:%M:%S')
        displaycolour = graphics.Color(255, 0, 0)
        self.showtext(clocktext, 0, 0, "8x13.bdf", displaycolour)

    def displaytimer(self):
        t = parser.parse(self.content)
        if t.hour == 0:
            timertext = t.strftime('%M:%S')
        else:
            timertext = t.strftime('%H:%M:%S')

        displaycolour = graphics.Color(255, 0, 0)
        self.showtext(timertext, 0, 0, "8x13.bdf", displaycolour)

    def displaymessage(self):
        displaycolour = graphics.Color(255, 255, 255)
        self.showtext(self.content, 0, 0, "8x13.bdf", displaycolour)

    def displayheartbeat(self):
        # FLASH ALL PIXELS ONTHE WIDGET
        t = datetime.now()
        ms = t.microsecond
        if ms % 1000 > 500:
            c = 255
        else:
            c = 0

        self.fillwidget(c)


# main function
if __name__ == "__main__":
    # initialise MQTT broker

    # initialise MQTT client
    print("welcome to the scoreboard")
    print(config.mqtt['host'])

    mqttclient = MyMQTTClient()
    mqttclient.start_connection(config.mqtt['host'],
                                config.mqtt['port'],
                                config.mqtt['keepalive_interval'],
                                config.mqtt['topic'])

    # initialise Matrix display
    sb_display = ScoreboardDisplay()

    # initialise screen widgets
    homescorewidget = DisplayWidget(sb_display, 5, 5, 5, 5, "0")
    awayscorewidget = DisplayWidget(sb_display, 5, 10, 5, 5, "0")
    clockwidget = DisplayWidget(sb_display, 0, 0, 64, 16, "12:00")
    timerwidget = DisplayWidget(sb_display, 0, 0, 64, 16, "10:09")
    messagewidget = DisplayWidget(sb_display, 0, 0, 64, 16, "Hello World")
    heartbeatwidget = DisplayWidget(sb_display, 0, 0, 1, 1, "0")

# loop


while True:
    sb_display.offscreen_canvas.Clear()
    print("clear screen")

    # clear the display

    # set active widgets
    homescorewidget.displayscore()
    print("next")
    awayscorewidget.displayscore()
    print("now the clock")
    clockwidget.displayclock()
    print("now the timer")
    timerwidget.displaytimer()
    print("now the heartbeat")
    heartbeatwidget.displayheartbeat()

    # wait a short time
    time.sleep(0.05)

    # refresh the display
    sb_display.offscreen_canvas = sb_display.matrix.SwapOnVSync(sb_display.offscreen_canvas)


    # repeat
