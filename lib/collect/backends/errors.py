#
# Common backend errors.
#

class BackendRecordError(Exception):
    pass

class BackendBackupError(Exception):
    pass

class BackendInvalidPayloadError(Exception):
    pass
