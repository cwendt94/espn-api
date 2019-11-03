import logging
import sys

def setup_logger(debug=False) -> logging:
    '''Setups Debug Logger'''
    level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger('League')

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

