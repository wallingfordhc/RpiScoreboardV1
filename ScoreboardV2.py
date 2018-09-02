#!/usr/bin/env python
#
# Scoreboard created originally for Wallingford Hockey Club - June 2018
#
# v.0.3
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

# does this firce an analysis


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
        print("Received: ")
        self.message_handler(msg)

    def message_handler(self, msg):
        message_raw = msg.payload.decode("utf-8", "ignore")
        message_verb, message_value = message_raw.split(';')

        if message_verb == "homescore":
            self.homescore(message_value)

        if message_verb == "awayscore":
            self.awayscore(message_value)

        if message_verb == "setmessage":
            self.setmessage(message_value)

        if message_verb == "showscore":
            self.showscore(message_value)

        if message_verb == "showtimer":
            self.showtimer(message_value)

        if message_verb == "settimer":
            self.settimer(message_value)

        if message_verb == "pausetimer":
            self.pausetimer(message_value)

        if message_verb == "starttimer":
            self.starttimer(message_value)

        if message_verb == "showclock":
            self.showclock(message_value)

        if message_verb == "showmessage":
            self.showmessage(message_value)

        if message_verb == "scrollspeed":
            self.setscrollspeed(message_value)

        # TODO ADD MORE IF BRANCHES

    def homescore(self, score):
        # dont let the score be negative
        if score < 0:
            score = 0
        homescorewidget.content = score

    def awayscore(self, score):
        # dont let the score be negative
        if score < 0:
            score = 0
        awayscorewidget.content = score

    def setmessage(self, message_text):
        messagewidget.content = message_text

    def showscore(self, set_visibility):
        set_visibilityb = bool(set_visibility)
        print(set_visibilityb)
        awayscorewidget.is_visible = set_visibilityb
        homescorewidget.is_visible = set_visibilityb

    def showtimer(self, set_visibility):
        set_visibilityb = bool(set_visibility)
        print(set_visibilityb)
        timerwidget.is_visible = set_visibilityb

    def showclock(self, set_visibility):
        set_visibilityb = bool(set_visibility)
        print(set_visibilityb)
        clockwidget.is_visible = set_visibilityb

    def showmessage(self, set_visibility):
        set_visibilityb = bool(set_visibility)
        print(set_visibilityb)
        messagewidget.is_visible = set_visibilityb

    def settimer(self, timer_value):

        timerwidget.is_running = False
        timerwidget.timerlength = parser.parse(timer_value)
        timerwidget.displaytime = parser.parse(timer_value)

    def starttimer(self, timer_value):

        timerwidget.starttime = datetime.now()

        if timer_value:
            timerwidget.timerlength = parser.parse(timer_value)
        else:
            timerwidget.timerlength = timerwidget.displaytime

        timerwidget.is_running = True

    def pausetimer(self, timer_value):

        timerwidget.is_running = False
        if timer_value:
            timerwidget.timerlength = parser.parse(timer_value)

class ScoreboardDisplay:

    def __init__(self):
        options = RGBMatrixOptions()
        # TODO MOVE TO CONFIG FILE
        options.hardware_mapping = "adafruit-hat"
        options.disable_hardware_pulsing = True
        options.rows = 16
        options.cols = 32
        options.chain_length = 4
        options.pixel_mapper_config = "U-mapper"
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
        self.is_running = False

        self.displayfont = graphics.Font()
        self.displayfont.LoadFont("/home/pi/fonts/" + "8x13.bdf")
        self.starttime = datetime.now()
        self.displaytime = datetime.strptime('35:00', '%M:%S')
        self.timerlength = datetime.strptime('35:00', '%M:%S')
        self.status = "paused"
        self.scrollspeed = 10
        self.scrollstatus = "stopped"

    def showtext(self, text, xx, yy, font, displaycolour):
        xpos = 0
        messagelength = 0
        for character in text:
            messagelength += self.displayfont.CharacterWidth(ord(character))
        # if the message is longer than the widget - start it off the screen
        # and scroll all the way to the end in the time set by scrollspeed
        if messagelength > self.xwidth:
            elapsedseconds = (datetime.now()-self.starttime).total_seconds()
            xpos = self.xwidth - (elapsedseconds % self.scrollspeed)*((self.xwidth+messagelength) / self.scrollspeed)

        length = graphics.DrawText(self.parentdisplay.offscreen_canvas,
                                   self.displayfont,
                                   self.x + xx + xpos, self.y + yy,
                                   displaycolour, text)

    def showimage(self, image, xx, yy):
        self.parentdisplay.offscreen_canvas.SetImage(image, self.x + xx, self.y + yy)

    def fillwidget(self, colour):
        for i in range(self.x, self.x + self.xwidth - 1):
            for j in range(self.y, self.y + self.ywidth - 1):
                self.parentdisplay.offscreen_canvas.SetPixel(i, j, colour, 0, 0)

    def displayscore(self):

        digits = {'0': "imgs/number0r.png",
                  '1': "imgs/number1r.png",
                  '2': "imgs/number2r.png",
                  '3': "imgs/number3r.png",
                  '4': "imgs/number4r.png",
                  '5': "imgs/number5r.png",
                  '6': "imgs/number6r.png",
                  '7': "imgs/number7r.png",
                  '8': "imgs/number8r.png",
                  '9': "imgs/number9r.png",
                  '10': "imgs/number10r.png",
                  '11': "imgs/number11r.png"
                  }

        scoreimage = Image.open(digits[self.content])
        self.showimage(scoreimage, 0, 0)

    def displayclock(self):
        if self.is_visible:
            t = datetime.now()
            clocktext = t.strftime('%H:%M:%S')
            # print("showing clock" + clocktext)
            displaycolour = graphics.Color(255, 0, 0)
            self.showtext(clocktext, 0, 13, "8x13.bdf", displaycolour)

    def displaytimer(self):
        if self.is_visible:
            if self.is_running:
                self.displaytime = self.timerlength - (datetime.now() - self.starttime)
            if self.displaytime <= 0:
                self.displaytime = 0
            if self.displaytime.hour == 0:
                timertext = self.displaytime.strftime('%M:%S')
            else:
                timertext = self.displaytime.strftime('%H:%M:%S')

            displaycolour = graphics.Color(255, 0, 0)
            self.showtext(timertext, 0, 14, "8x13.bdf", displaycolour)
        else:
            pass  # don't show anything if its not visible

    def displaymessage(self):
        if self.is_visible:
            displaycolour = graphics.Color(255, 255, 255)
            self.showtext(self.content, 0, 14, "8x13.bdf", displaycolour)

    def displayheartbeat(self):
        if self.is_visible:
            # FLASH ALL PIXELS ONTHE WIDGET
            t = datetime.now()
            ms = t.microsecond
            if ms % 1000000 > 400000:
                c = 255
            else:
                c = 0
            self.fillwidget(c)


# main function
if __name__ == "__main__":
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
    homescorewidget = DisplayWidget(sb_display, 0, 16, 32, 16, "0")
    awayscorewidget = DisplayWidget(sb_display, 32, 16, 32, 16, "0")
    clockwidget = DisplayWidget(sb_display, 0, 0, 64, 16, "12:00")
    timerwidget = DisplayWidget(sb_display, 14, -2, 64, 16, "00:00:00", False)
    messagewidget = DisplayWidget(sb_display, 0, 0, 64, 16, "Hello Wallingford", False)
    heartbeatwidget = DisplayWidget(sb_display, 0, 0, 2, 2, "0")

# loop


while True:
    sb_display.offscreen_canvas.Clear()
    # print("clear screen")

    # clear the display

    # set active widgets
    homescorewidget.displayscore()
    # print("next")
    awayscorewidget.displayscore()
    # print("now the clock")
    clockwidget.displayclock()
    # print("now the timer")
    timerwidget.displaytimer()
    # print("now the heartbeat")
    heartbeatwidget.displayheartbeat()
    # print ("and a message?")
    messagewidget.displaymessage()

    # wait a short time
    #  time.sleep(0.02)

    # refresh the display
    sb_display.offscreen_canvas = sb_display.matrix.SwapOnVSync(sb_display.offscreen_canvas)

    # repeat
