import lib.collect.config as config

if config.BACKEND == 'dynamodb':
    import lib.collect.backends.dymamodb as api
else:
    import lib.collect.backends.localfs as api
