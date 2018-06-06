#!/usr/bin/env python
# Display a runtext with double-buffering.
#


import paho.mqtt.client as mqtt
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
import time
import argparse
import sys

# Define Variables
MQTT_HOST = "192.168.1.92"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "scoreboard/1"
messagetxt = "It works!"
# Define on connect event function
# We shall subscribe to our Topic in this function
def on_connect(self, mosq, obj, rc):
    mqttc.subscribe(MQTT_TOPIC, 0)
    print("Connect on " + MQTT_HOST)


# Define on_message event function.
# This function will be invoked every time,
# a new message arrives for the subscribed topic
def on_message(mosq, obj, msg):
    global messagetxt
    messagetxt = msg.payload


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed to Topic: " +
          MQTT_TOPIC + " with QoS: " + str(granted_qos))


class RunText:
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
    def run(self):

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/fonts/7x13.bdf")
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width
        my_text = self.args.text

        # infinite loop
        while True:
            # clear the offscreen canvas
            offscreen_canvas.Clear()
            if messagetxt:
                my_text = messagetxt

            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    def process(self):
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
        if self.args.led_slowdown_gpio != None:
            options.gpio_slowdown = self.args.led_slowdown_gpio

        # initialise the matrix
        self.matrix = RGBMatrix(options=options)

        # Initiate MQTT Client
        mqttc = mqtt.Client()

        # Assign event callbacks
        mqttc.on_message = on_message
        mqttc.on_connect = on_connect
        mqttc.on_subscribe = on_subscribe

        # Connect with MQTT Broker
        mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

        # call the main part of the program
        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            self.run()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        return True


# Main function
if __name__ == "__main__":
    run_text = RunText()
    run_text.process()
