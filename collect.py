#!/usr/bin/env python

import datetime
from distutils.dir_util import mkpath
import json
import os
import time
import socket
import sys
import uuid

import RPi.GPIO as GPIO
from picamera import PiCamera
import pytz
from pytz import timezone

import lib.ext.dht11 as dht11

import lib.collect.config as config
import lib.collect.backend as backend

WORK_DIR = config.WORK_DIR
COLLECT_API_LOG = config.COLLECT_API_LOG

API_VERSION = 0

CLIENT_ID = 0
CLIENT_VERSION = 0
CLIENT_MODEL = 'mark0'

CAMERA_MODEL = 'Kuman SC15-JP'
LED_MODEL = 'cheap'
SENSOR_TEMPERATURE_MODEL = 'DHT-11'
SENSOR_HUMIDITY_MODEL = 'DHT-11'
DHT_PIN = 15


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()


def snapshot():
    name = '.'.join([
        datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        str(uuid.uuid4()),
        'jpg'
    ])
    path = os.path.sep.join([WORK_DIR, name])
    camera = PiCamera()
    camera.start_preview()
    time.sleep(5)
    camera.capture(path)
    camera.stop_preview()
    payload = {
        'm': CAMERA_MODEL,
        'u': 'jpg',
        'v': name,
    }
    return payload, path


def cmd_leds(turn_red_on = True, turn_blue_on = True):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_address = config.LEDS_D_ADDRESS
    result = {}
    try:
        sock.connect(server_address)
        try:
            message = json.dumps({ 'red': turn_red_on, 'blue': turn_blue_on })
            print("Send to socket: %s" % message)
            sock.sendall(message)

            # TODO Get confirmation from daemon
            #amount_received = 0
            #amount_expected = len(message)
            #while amount_received < amount_expected:
            #    data = sock.recv(16)
            #    amount_received += len(data)
            # result['red'] = ...
            # result['blue'] = ...
            result['red'] = {
                'm': LED_MODEL,
                'u': 'bool',
                'v': turn_red_on,
            }
            result['blue'] = {
                'm': LED_MODEL,
                'u': 'bool',
                'v': turn_blue_on,
            }
        finally:
            sock.close()
        return result
    except socket.error:
        print("Could not UDS communicate with LED daemon.")


def sensor_harvest():
    # For now, just DHT11
    instance = dht11.DHT11(pin=DHT_PIN)
    result = instance.read()
    if result.is_valid():
        return {
            'temperature': {
                'm': SENSOR_TEMPERATURE_MODEL,
                'u': 'celsius',
                'v': result.temperature,
            },
            'humidity': {
                'm': SENSOR_HUMIDITY_MODEL,
                'u': 'percent',
                'v': result.humidity,
            }
        }
    else:
        print("Could not read DHT11")
        return {}


def backup(img_file):
    backend.api.backups([img_file])


def post(data):
    data['client'] = {
        'v': CLIENT_VERSION,
        'i': CLIENT_ID,
        'm': CLIENT_MODEL,
    }
    data['api'] = API_VERSION
    backend.api.record(data)


def run():
    # 1) Take snapshot
    # 2) Send snapshot to Cx Images, unique name
    # 3) Send status data to Cx API.

    # Decide
    z = timezone('Asia/Tokyo')
    local_time = datetime.datetime.now(z).time()
    night_start = datetime.time(21)
    night_end = datetime.time(4)
    if local_time > night_start or local_time < night_end:
        turn_on_leds = True
    else:
        turn_on_leds = False

    camera, full_path = snapshot()
    sensors = sensor_harvest()
    leds = cmd_leds(turn_blue_on=turn_on_leds, turn_red_on=turn_on_leds)

    state = {
        'camera': camera,
        'leds': leds,
    }
    state.update(sensors)

    post({
      'ts': datetime.datetime.now().isoformat(),
      'state': state
    })
    backup(full_path)
    if os.path.exists(full_path):
        os.remove(full_path)


if __name__ == '__main__':
    run()
