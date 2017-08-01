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
from pytz import timezone
import ntplib

import lib.ext.dht11 as dht11
import lib.ext.mg811 as mg811

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
FAN_MODEL = 'cheap'

SENSOR_TEMPERATURE_MODEL = 'DHT-11'
SENSOR_HUMIDITY_MODEL = 'DHT-11'
DHT_PIN = 15

SENSOR_CO2_MODEL = 'MG-811'
MG811_PIN = 8

SENSORS = [
    'dht11',
    'mg811',
]

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
        'v': os.path.sep.join([
                        str(CLIENT_ID),
                        str(CLIENT_MODEL),
                        str(CLIENT_VERSION),
                        name,
                     ]),
    }
    return payload, path


def cmd(turn_red_on = True, turn_blue_on = True):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_address = config.DEVICES_D_ADDRESS
    result = {}
    try:
        sock.connect(server_address)
        try:
            message = json.dumps({
                'reds': turn_red_on,
                'blues': turn_blue_on,
            })
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
            result['leds'] = {}
            result['leds']['red'] = {
                'm': LED_MODEL,
                'u': 'bool',
                'v': turn_red_on,
            }
            result['leds']['blue'] = {
                'm': LED_MODEL,
                'u': 'bool',
                'v': turn_blue_on,
            }
            #result['fan'] = {
            #    'm': FAN_MODEL,
            #    'u': 'bool',
            #    'v': turn_fan_on,
            #}
        finally:
            sock.close()
        return result
    except socket.error:
        print("Could not UDS communicate with LED daemon.")


def sensor_harvest():
    readings = {}
    for sensor in SENSORS:
        readings.update(eval("harvest_" + sensor + "()"))
    return readings


def harvest_mg811():
    instance = mg811.MG811(MG811_PIN)
    result = instance.read()
    return {
        'co2': {
            'm': SENSOR_CO2_MODEL,
            'u': 'relative',
            'v': result.raw(),
        }
    }


def harvest_dht11():
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


def backup(img_file, key):
    backend.api.backups([img_file], [key])


def post(data):
    data['client'] = {
        'v': CLIENT_VERSION,
        'i': CLIENT_ID,
        'm': CLIENT_MODEL,
    }
    data['api'] = API_VERSION
    backend.api.record(data)


def run():
    # Get local time
    try:
        time_client = ntplib.NTPClient()
        response = time_client.request('pool.ntp.org')
        local_time = datetime.datetime.fromtimestamp(response.tx_time)
    except:
        local_time = datetime.datetime.now()
    night_start = datetime.time(21)
    night_end = datetime.time(4)
    if local_time.time() > night_start or local_time.time() < night_end:
        turn_on_leds = True
    else:
        turn_on_leds = False

    camera, full_path = snapshot()
    sensors = sensor_harvest()

    #if sensors['co2']['v'] > 0 and mg811.MG811Result(sensors['co2']['v']).compared_to_air() == 'low':
    #    turn_fan_on=True
    #else:
    #    turn_fan_on=False

    cmd_results = cmd(
        turn_blue_on=turn_on_leds,
        turn_red_on=turn_on_leds
    )

    state = {
        'camera': camera,
        'leds': cmd_results['leds'],
    }
    state.update(sensors)

    post({
      'ts': datetime.datetime.utcnow().isoformat(),
      'state': state
    })
    backup(full_path, camera['v'])
    if os.path.exists(full_path):
        os.remove(full_path)


if __name__ == '__main__':
    run()
