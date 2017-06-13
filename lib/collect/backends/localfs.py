from distutils.dir_util import mkpath
import json
import os
from shutil import copyfile

import lib.collect.backends.errors as errors
import lib.collect.config as config


def record(payload):
    try:
        pl = json.dumps(payload)
        with open(config.COLLECT_API_LOG, 'a') as f:
            f.write(pl + "\n")
    except Exception as e:
        raise errors.BackendRecordError(e)


def backups(files = [], keys = []):
    try:
        for idx, f in enumerate(files):
            key = keys[idx]
            target_dir = os.path.sep.join([
                config.BACKUP_DIR,
                os.path.dirname(key),
            ])
            mkpath(target_dir)
            target = os.path.sep.join([
                target_dir,
                os.path.basename(key)
            ])
            copyfile(f, target)
    except Exception as e:
        raise errors.BackendBackupError(e)
