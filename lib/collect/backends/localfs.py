import os
from shutil import copyfile

import lib.collect.config as config

def record(payload):
    with open(config.COLLECT_API_LOG, 'a') as f:
        f.write(payload + "\n")

def backups(files = []):
    for f in files:
        target = os.path.sep.join([config.BACKUP_DIR, os.path.basename(f)])
        copyfile(f, target)
