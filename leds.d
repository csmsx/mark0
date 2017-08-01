#!/usr/bin/env python

from distutils.dir_util import mkpath
import json
import socket
import sys
import os

import daemon
from gpiozero import LED, DigitalOutputDevice

import lib.collect.config as config

RUN_DIR = config.LEDS_D_RUN_DIR

LOG_DIR = '/var/log/mark0/leds.d'
mkpath(LOG_DIR)
OUT_LOG=os.path.sep.join([LOG_DIR, 'out.log'])
ERR_LOG=os.path.sep.join([LOG_DIR, 'err.log'])

BLUE_LED_PINS = [ 18, 23 ]
RED_LED_PINS = [ 17, 22 ]

FAN_PINS = [ 21 ]


def log(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def __apply(obj, turn_on):
    if turn_on:
        obj.on()
    else:
        obj.off()


def run(leds):
    log("leds.d starting...")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(config.LEDS_D_ADDRESS)
    sock.listen(1)
    log("leds.d listening at %s" % config.LEDS_D_ADDRESS)
    while True:
        conn, _ = sock.accept()
        log("leds.d got message")
        try:
            payload = ''
            while True:
                data = conn.recv(16)
                if data:
                    payload = payload + data
                else:
                    break
            try:
                log("leds.d received: %s" % payload)
                request = json.loads(payload)
                for k, values in leds.iteritems():
                    for v in values:
                        __apply(v, request[k])
            except ValueError:
                log("Failed to parse payload: %s" % payload)
        finally:
            conn.close()
    log("leds.d stopped listening at %s" % config.LEDS_D_ADDRESS)
    log("collect.d stopped")


with open(OUT_LOG, 'w+') as out_f:
    with open(ERR_LOG, 'w+') as err_f:
        with daemon.DaemonContext(
                                     working_directory=RUN_DIR,
                                     stdout=out_f,
                                     stderr=err_f
                                 ):
            try:
                os.unlink(config.LEDS_D_ADDRESS)
            except OSError:
                if os.path.exists(config.LEDS_D_ADDRESS):
                    raise
            leds = {
                'reds': [ LED(rl) for rl in RED_LED_PINS ],
                'blues': [ LED(bl) for bl in BLUE_LED_PINS ],
            }
            try:
                run(leds)
            finally:
                for device_list in leds.values():
                    for device in device_list:
                        device.close()
