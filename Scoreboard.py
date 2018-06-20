#!/usr/bin/env python
# Display a runtext with double-buffering.
#


import paho.mqtt.client as mqtt
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
from PIL import Image
import time
import datetime
import argparse
import sys
from dateutil import parser


# Define key CONSTANT Variables
MQTT_HOST = "192.168.1.92"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "scoreboard"


# define some global variables
# TODO remove the global variables
message_raw = "Welcome to the Scoreboard"
message_content = ""
message_value = ""
home = "0"
away = "0"
timerset = ""
clocktime = datetime.datetime.now()
starttime = datetime.datetime.now()
direction = "clock"






# Define on connect event function
# We shall subscribe to our Topic in this function
def on_connect(self, mosq, obj, rc):
    print("trying to subscribe")
    mqttc.subscribe(MQTT_TOPIC, 0)
    print("Connect on " + MQTT_HOST)

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed to Topic: " +
          MQTT_TOPIC + " with QoS: " + str(granted_qos))

# Define on_message event function.
# This function will be invoked every time,
# a new message arrives for the subscribed topic
def on_message(mosq, obj, msg):
    print("received  ")
    print(msg.payload)
    global message_raw, message_content, message_value
    message_raw = msg.payload.decode("utf-8", "ignore")
    message_content, message_value = message_raw.split(';')

    if message_content == "homescore":
        homescore(message_value)

    if message_content == "awayscore":
        awayscore(message_value)

    if message_content == "timerset":
        settimer(message_value)

    action = {
        "homescore": homescore,
        "awayscore": awayscore,
        "timerset": settimer,
        "timerstart": starttimer,
        "timerpause": pausetimer,
        "showmessage": showmessage,
        "hidemessage": hidemessage,
        "showclock": hideclock,
    }




# define the actions to take given certain messages
def homescore(score):
    global home
    print("updated home score")
    home = score


def awayscore(score):
    global away
    print("updated away score")
    away = score


def settimer(timer_value):
    global clocktime, starttime, direction
    print("set timer")
    clocktime = parser.parse(timer_value)
    starttime = datetime.datetime.now()
    direction = "down"


def starttimer(timer_value):
    pass


def pausetimer():
    pass


def hidetimer():
    pass


def showmessage(message):
    pass


def hidemessage():
    pass


def showclock():
    global direction
    print("show clock")
    direction = "clock"



def hideclock():
    pass


class MatrixDisplay:

    # Initialise and get arguments
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")
        self.parser.add_argument("-r", "--led-rows", action="store",
                                 help="Display rows. 16 for 16x32, 32 for 32x32. Default: 16", default=16, type=int)
        self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)",
                                 default=32, type=int)
        self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 4.",
                                 default=4, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store",
                                 help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("-p", "--led-pwm-bits", action="store",
                                 help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store",
                                 help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping",
                                 help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm",
                                 choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
        self.parser.add_argument("--led-scan-mode", action="store",
                                 help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)",
                                 default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store",
                                 help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130",
                                 default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true",
                                 help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store",
                                 help="Slow down writing to GPIO. Range: 1..100. Default: 1", choices=range(3),
                                 type=int)
        self.parser.add_argument("--led-no-hardware-pulse", action="store",
                                 help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store",
                                 help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB",
                                 type=str)
        self.parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"",
                                 default="U-mapper", type=str)
        self.parser.add_argument("--led-row-addr-type", action="store",
                                 help="0 = default; 1=AB-addressed panels;2=row direct", default=0, type=int,
                                 choices=[0, 1, 2])
        self.parser.add_argument("--led-multiplexing", action="store",
                                 help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven (Default: 8)",
                                 default=8, type=int)

    # define the main part of the program
    def scroll(self):

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        scorefont = graphics.Font()
        scorefont.LoadFont("/home/pi/fonts/10x20.bdf")
        scorefont.CharacterWidth(16)
        clockfont = graphics.Font()
        clockfont.LoadFont("/home/pi/fonts/8x13.bdf")
        hometextcolour = graphics.Color(255, 255, 255)
        awaytextcolour = graphics.Color(255, 255, 255)
        clocktextcolour = graphics.Color(255, 0, 0)
        timertextcolour = graphics.Color(255, 0, 0)
        awayxpos = 47
        awayypos = 31
        homexpos = 12
        homeypos = 31
        clockxpos = 0
        clockypos = 13
        timerxpos = 0
        timerypos = 13

        home_score = "0"
        away_score = "5"
        clock_text = "welcome"
        global direction
        global clocktime
        global starttime
        direction = "clock"
        clocktime = 0


        # infinite loop
        while True:
            # clear the offscreen canvas
            offscreen_canvas.Clear()
            if away:
                away_score = away
                length = graphics.DrawText(offscreen_canvas, scorefont, awayxpos, awayypos, hometextcolour, away_score)

            if home:
                home_score = home
                length = graphics.DrawText(offscreen_canvas, scorefont, homexpos, homeypos, awaytextcolour, home_score)

            if direction == "clock":
                t = datetime.datetime.now()
                clock_text = t.strftime('%H:%M:%S')
                length = graphics.DrawText(offscreen_canvas, clockfont, clockxpos, clockypos, clocktextcolour,
                                           clock_text)
            if direction == "down":
                t = clocktime - (datetime.datetime.now() - starttime)
                # add if timer < 2 mins pause
                timer_text = t.strftime('%H:%M:%S')
                length = graphics.DrawText(offscreen_canvas, clockfont, timerxpos, timerypos, timertextcolour,
                                           timer_text)


            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


    def Setup(self):
        # set up the matrix configuration based on the run time arguments
        self.args = self.parser.parse_args()

        options = RGBMatrixOptions()

        options.hardware_mapping = "adafruit-hat"
        options.disable_hardware_pulsing = True

        options.rows = self.args.led_rows
        options.cols = self.args.led_cols
        options.chain_length = self.args.led_chain
        options.parallel = self.args.led_parallel
        options.row_address_type = self.args.led_row_addr_type
        options.multiplexing = self.args.led_multiplexing
        options.pwm_bits = self.args.led_pwm_bits
        options.brightness = self.args.led_brightness
        options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.args.led_rgb_sequence
        options.pixel_mapper_config = self.args.led_pixel_mapper
        if self.args.led_show_refresh:
            options.show_refresh_rate = 1
        if self.args.led_slowdown_gpio is not None:
            options.gpio_slowdown = self.args.led_slowdown_gpio

        # initialise the matrix
        self.matrix = RGBMatrix(options=options)

        # call the main part of the program
        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            self.scroll()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        return True


# Main function
if __name__ == "__main__":
    mqttc = mqtt.Client()
    # Assign event callbacks
    mqttc.on_message = on_message
    message_raw = mqttc.on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe
    # Connect with MQTT Broker
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()
    run_text = MatrixDisplay()
    run_text.Setup()
