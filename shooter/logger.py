import logging


def logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.WARNING)
    formatter = logging.Formatter('[%(levelname)s:%(name)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

