import logging


def get_logger(name, debug=False, info=True):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.captureWarnings(True)
    logger.setLevel(logging.WARNING)
    if info:
        logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
    return logger
