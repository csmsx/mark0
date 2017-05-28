from distutils.dir_util import mkpath
import os

COLLECT_D_WORK_DIR = '/home/pi/cosmosx/mark0/collect.d'
mkpath(COLLECT_D_WORK_DIR)
SERVER_ADDRESS = os.path.sep.join([COLLECT_D_WORK_DIR, 'collect_d_socket'])
