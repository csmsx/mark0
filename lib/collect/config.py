from distutils.dir_util import mkpath
from os import path

WORK_DIR = path.expanduser('~/mark0/data')
mkpath(WORK_DIR)

BACKUP_DIR = path.sep.join([WORK_DIR, 'backups'])
mkpath(BACKUP_DIR)

COLLECT_API_LOG = path.sep.join([WORK_DIR, 'collect_api_log.json'])

DEVICES_D_RUN_DIR = "/var/log/mark0/devices.d"
mkpath(DEVICES_D_RUN_DIR)
DEVICES_D_ADDRESS = path.sep.join([DEVICES_D_RUN_DIR, "devices_d_socket"])

BACKEND = 'aws'

DYNAMODB_TABLE_NAME = 'mark0_observations'
DYNAMODB_KEY_RESERVED_CHARACTER = '#'

S3_BUCKET = 'plant-data-mark0'
