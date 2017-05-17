#!/usr/bin/env python

from distutils.dir_util import mkpath
import json
import socket
import sys
import os

import daemon
from gpiozero import LED

WORK_DIR = '/tmp/cosmosx/mark0/collect.d'
mkpath(WORK_DIR)
OUT_LOG=os.path.sep.join([WORK_DIR, 'out.log'])
ERR_LOG=os.path.sep.join([WORK_DIR, 'err.log'])

SERVER_ADDRESS = os.path.sep.join([WORK_DIR, 'collect_d_socket'])

BLUE_LED_PIN = 18
RED_LED_PIN = 17

def red(turn_on = True):
    red = LED(RED_LED_PIN)
    try:
        if turn_on:
            red.on()
        else:
            red.off()
    finally:
        red.close()


def run():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SERVER_ADDRESS)
    sock.listen(1)
    while True:
        conn, _ = sock.accept()
        try:
            payload = ''
            while True:
                data = conn.recv(16)
                if data:
                    payload = payload + data
                else:
                    break
            try:
              request = json.loads(payload)
              red(request['red'])
            except ValueError:
                print("Failed to parse payload: %s" % payload)
        finally:
            conn.close()


with open(OUT_LOG, 'w+') as out_f:
    with open(ERR_LOG, 'w+') as err_f:
        with daemon.DaemonContext(
                                     working_directory=WORK_DIR,
                                     stdout=out_f,
                                     stderr=err_f
                                 ):
            try:
                os.unlink(SERVER_ADDRESS)
            except OSError:
                if os.path.exists(SERVER_ADDRESS):
                    raise
            run()
