#!/usr/bin/env python

from distutils.dir_util import mkpath
import json
import socket
import sys
import os

import daemon
from gpiozero import LED

import lib.collect.config as config

WORK_DIR = config.COLLECT_D_WORK_DIR
OUT_LOG=os.path.sep.join([WORK_DIR, 'out.log'])
ERR_LOG=os.path.sep.join([WORK_DIR, 'err.log'])

BLUE_LED_PIN = 18
RED_LED_PIN = 17


def log(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def run(leds):
    log("collect.d starting...")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(config.SERVER_ADDRESS)
    sock.listen(1)
    log("collect.d listening at %s" % config.SERVER_ADDRESS)
    while True:
        conn, _ = sock.accept()
        log("collect.d got message")
        try:
            payload = ''
            while True:
                data = conn.recv(16)
                if data:
                    payload = payload + data
                else:
                    break
            try:
                log("collect.d received: %s" % payload)
                request = json.loads(payload)
                log("collect.d parsed: %s" % str(payload))
                if request['red']:
                    leds['red'].on()
                else:
                    leds['red'].off()
            except ValueError:
                log("Failed to parse payload: %s" % payload)
        finally:
            conn.close()
    log("collect.d stopped listening at %s" % config.SERVER_ADDRESS)
    log("collect.d stopped")


with open(OUT_LOG, 'w+') as out_f:
    with open(ERR_LOG, 'w+') as err_f:
        with daemon.DaemonContext(
                                     working_directory=WORK_DIR,
                                     stdout=out_f,
                                     stderr=err_f
                                 ):
            try:
                os.unlink(config.SERVER_ADDRESS)
            except OSError:
                if os.path.exists(config.SERVER_ADDRESS):
                    raise
            leds = {
                'red': LED(RED_LED_PIN),
                'blue': LED(BLUE_LED_PIN),
            }
            try:
                run(leds)
            finally:
                for led in leds.values():
                    led.close()
