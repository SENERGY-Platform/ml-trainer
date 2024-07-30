import logging 
import sys 

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    return logger

logging_levels = {
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'debug': logging.DEBUG
}


class LoggerError(Exception):
    def __init__(self, arg):
        super().__init__(f"unknown log level '{arg}'")

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(fmt="%(levelname)s: %(message)s"))

logger = logging.getLogger('uvicorn.error')
logger.propagate = False
logger.addHandler(handler)


def init_logger(level):
    if level not in logging_levels.keys():
        raise LoggerError(level)
    log_level = logging_levels[level]
    logger.setLevel(log_level)
    logging.basicConfig(stream=sys.stdout, level=log_level)