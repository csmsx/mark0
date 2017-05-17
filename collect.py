#!/usr/bin/env python

import datetime
from distutils.dir_util import mkpath
import json
import os
import time
import uuid

import RPi.GPIO as GPIO
from gpiozero import LED
from picamera import PiCamera

import lib.ext.dht11

WORK_DIR = '/tmp/cosmosx/mark0'
mkpath(WORK_DIR)
MEMO_FILE = os.path.sep.join([WORK_DIR, 'last'])

API_VERSION = 0

CLIENT_MODEL = 'mark0'
CLIENT_VERSION = 0
BLUE_LED_PIN = 18
RED_LED_PIN = 17
DHT_PIN = 15


#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()


def snapshot():
    name = str(uuid.uuid4()) + '.jpg'
    path = os.path.sep.join([WORK_DIR, name])
    camera = PiCamera()
    camera.start_preview()
    time.sleep(5)
    camera.capture(path)
    camera.stop_preview()
    return name, path


def toggle_leds():
    red = LED(RED_LED_PIN)
    blue = LED(BLUE_LED_PIN)
    status = {}
    try:
        red.toggle()
        blue.toggle()
        status['red'] = red.is_lit
        status['blue'] = blue.is_lit
    finally:
        red.close()
        blue.close()
    return status


def sensor_harvest():
    # For now, just DHT11
    instance = dht11.DHT11(pin=DHT_PIN)
    result = instance.read()
    if result.is_valid():
        return {
            'temperature': result.temperature,
            'humidity': result.humidity,
        }
    else:
        print("Could not read DHT11")
        return {}


def backup(img_file):
    pass


def post(data):
    data['client'] = { 'm': CLIENT_MODEL, 'v': CLIENT_VERSION }
    data['api'] = API_VERSION
    payload = json.dumps(data)
    print(payload)
    # TODO


def run():
    '''
    memo = {
      'ts': Timestamp of the last operation
      'leds': Supposed state of the LEDS: {
        'blue': { state: True/False, until: xyz }
        'red':  { state: True/False, until: xyz }
      }
    }
    '''
    memo = {}
    if os.path.isfile(MEMO_FILE):
        with open(MEMO_FILE, 'r') as f:
            memo = json.loads(f.read())

    # 1) Take snapshot
    # 2) Send snapshot to Cx Images, unique name
    # 3) Send status data to Cx API.

    img_name, full_path = snapshot()
    leds = toggle_leds()
    sensors = sensor_harvest()
    post({
      'snapshot': img_name,
      'ts': datetime.datetime.now().isoformat(),
      'status': {
        'leds': leds,
        'sensors': sensors,
      }
    }

if __name__ == '__main__':
    run()
