from distutils.dir_util import mkpath
import os

LEDS_D_RUN_DIR = '/var/log/mark0/leds.d'
mkpath(LEDS_D_RUN_DIR)
SERVER_ADDRESS = os.path.sep.join([LEDS_D_RUN_DIR, 'leds_d_socket'])
