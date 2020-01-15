import logging
import os


def get_logger(name, level=None):
    logger = logging.getLogger(name)
    log_env = os.getenv('loglevel') or 0
    loglevel = level or int(log_env) or logging.INFO
    logger.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
