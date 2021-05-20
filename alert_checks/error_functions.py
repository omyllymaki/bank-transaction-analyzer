import logging

logger = logging.getLogger(__name__)


class AlertException(Exception):
    pass

def log_error(name, value, expected):
    logger.error(f"Check {name} doesn't pass: calculated {value}; expected {expected}")


def log_error_and_raise_exception(name, value, expected):
    logger.error(f"Check {name} doesn't pass: calculated {value}; expected {expected}")
    raise AlertException("Check doesn't pass. The program will be terminated.")