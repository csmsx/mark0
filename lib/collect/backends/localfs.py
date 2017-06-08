import lib.collect.config as config

def record(payload):
    with open(config.COLLECT_API_LOG, 'a') as f:
        f.write(payload + "\n")
