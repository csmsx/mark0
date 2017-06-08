from distutils.dir_util import mkpath
import os

WORK_DIR = os.path.expanduser('~/mark0/data')
mkpath(WORK_DIR)

COLLECT_API_LOG = os.path.sep.join([WORK_DIR, 'collect_api_log.json'])

LEDS_D_RUN_DIR = '/var/log/mark0/leds.d'
mkpath(LEDS_D_RUN_DIR)
LEDS_D_ADDRESS = os.path.sep.join([LEDS_D_RUN_DIR, 'leds_d_socket'])
