import lib.collect.config as config

def record(payload):
    with open(config.COLLECT_API_LOG, 'w+') as f:
        f.write(to_save)
