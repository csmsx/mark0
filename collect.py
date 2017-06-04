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

WORK_DIR = '~/mark0/data'
mkpath(WORK_DIR)

COLLECT_API_LOG = os.path.sep.join([WORK_DIR, 'collect_api_log.json'])

API_VERSION = 0

CLIENT_MODEL = 'mark0'
CLIENT_VERSION = 0
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
    return name, path


def cmd_leds(turn_red_on = True, turn_blue_on = True):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_address = config.SERVER_ADDRESS
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
            result['red'] = turn_red_on
            result['blue'] = turn_blue_on
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

    original = []

    # TODO Temporary time to get the server up.
    if os.path.exists(COLLECT_API_LOG):
        with open(COLLECT_API_LOG, 'r') as f:
            payload = f.read()
            try:
                original = json.loads(payload)
            except ValueError:
                print("Could not parse %s, overwriting." % COLLECT_API_LOG)
                original = []

    original.append(data)
    to_save = json.dumps(original)
    with open(COLLECT_API_LOG, 'w') as f:
        f.write(to_save)

    # TODO


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

    img_name, full_path = snapshot()
    leds = cmd_leds(turn_blue_on=turn_on_leds, turn_red_on=turn_on_leds)
    sensors = sensor_harvest()
    post({
      'ts': datetime.datetime.now().isoformat(),
      'snapshot': img_name,
      'status': {
        'leds': leds,
        'sensors': sensors,
      }
    })
    #if os.path.exists(full_path):
    #    os.remove(full_path)


if __name__ == '__main__':
    run()
