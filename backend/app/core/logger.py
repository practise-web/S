import logging
from enum import StrEnum
from app.core.context import request_id_ctx

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(lineno)d"
LOG_FORMAT_PROD = "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s: %(message)s"



class LogLevels(StrEnum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True

def configure_logging(log_level : str = LogLevels.error) -> None:
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]
    if log_level not in log_levels:
        logging.basicConfig(level=LogLevels.error)
        return
    if log_level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return
    
    logging.basicConfig(level=log_level, format=LOG_FORMAT_PROD)
    for handler in logging.getLogger().handlers:
        handler.addFilter(RequestIdFilter())
    logging.getLogger().addFilter(RequestIdFilter())

