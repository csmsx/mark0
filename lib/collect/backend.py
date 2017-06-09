import lib.collect.config as config

try:
    if config.BACKEND == 'aws':
        import lib.collect.backends.aws as api
    else:
        import lib.collect.backends.localfs as api
except AttributeError:
    import lib.collect.backends.localfs as api
