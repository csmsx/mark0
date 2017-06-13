import os
from shutil import copyfile

import lib.collect.backends.errors as errors
import lib.collect.config as config


def record(payload):
    try:
        with open(config.COLLECT_API_LOG, 'a') as f:
            f.write(payload + "\n")
    except:
        raise errors.BackendRecordError(payload)


def backups(files = []):
    try:
        for f in files:
            target = os.path.sep.join([
                config.BACKUP_DIR,
                os.path.basename(f)
            ])
            copyfile(f, target)
    except:
        raise errors.BackendBackupError(payload)
