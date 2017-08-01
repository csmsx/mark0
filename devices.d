#!/usr/bin/env python

from distutils.dir_util import mkpath
import json
import socket
import sys
from os import path, unlink, remove

import daemon
import daemon.pidfile as pidfile
from gpiozero import LED, DigitalOutputDevice

import lib.collect.config as config

script_name = path.basename(__file__)

LOCK_DIR = "/var/lock/mark0/%s" % script_name
mkpath(LOCK_DIR)
DEVICES_D_LOCK = path.sep.join([LOCK_DIR, "%s.lock" % script_name])
if path.exists(DEVICES_D_LOCK):
    sys.stderr.write("Syslock exists. Cannot run two instances.")
    sys.exit(666)

RUN_DIR = config.DEVICES_D_RUN_DIR
DEVICES_D_ADDRESS = config.DEVICES_D_ADDRESS

LOG_DIR = "/var/log/mark0/%s" % script_name
mkpath(LOG_DIR)
OUT_LOG=path.sep.join([LOG_DIR, 'out.log'])
ERR_LOG=path.sep.join([LOG_DIR, 'err.log'])

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


def run(devices):
    log("%s starting..." % script_name)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(DEVICES_D_ADDRESS)
    sock.listen(1)
    log("%s listening at %s" % (script_name, DEVICES_D_ADDRESS))
    while True:
        conn, _ = sock.accept()
        log("%s got message" % script_name)
        try:
            payload = ''
            while True:
                data = conn.recv(16)
                if data:
                    payload = payload + data
                else:
                    break
            try:
                log("%s received: %s" % (script_name, payload))
                request = json.loads(payload)
                for k, values in devices.iteritems():
                    for v in values:
                        __apply(v, request[k])
            except ValueError:
                log("Failed to parse payload: %s" % payload)
        finally:
            conn.close()
    log("%s stopped listening at %s" % (script_name, DEVICES_D_ADDRESS))
    log("%s stopped" % script_name)


with open(OUT_LOG, 'w+') as out_f:
    with open(ERR_LOG, 'w+') as err_f:
        with daemon.DaemonContext(
                                     working_directory=RUN_DIR,
                                     pidfile=pidfile.TimeoutPIDLockFile(DEVICES_D_LOCK),
                                     stdout=out_f,
                                     stderr=err_f
                                 ):
            try:
                unlink(DEVICES_D_ADDRESS)
            except OSError:
                if path.exists(DEVICES_D_ADDRESS):
                    raise
            devices = {
                'reds': [ LED(rl) for rl in RED_LED_PINS ],
                'blues': [ LED(bl) for bl in BLUE_LED_PINS ],
            }
            try:
                run(devices)
            finally:
                for device_list in devices.values():
                    for device in device_list:
                        device.close()
                if path.exists(DEVICES_D_LOCK):
                    remove(DEVICES_D_LOCK)
