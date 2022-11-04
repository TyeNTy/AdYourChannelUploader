import logging
import logging.config
import os

def loadConfig() -> None:
    kiloBytes = 1024
    megaBytes = kiloBytes * 1024
    basePathLogs = "logs"

    if(not os.path.exists(basePathLogs)):
        os.mkdir(basePathLogs)

    MY_LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default_formatter': {
                'format': '[%(levelname)s:%(asctime)s] %(message)s',
                "datefmt":"%d-%m-%Y %I:%M:%S"
            },
        },
        'handlers': {
            'console': {
                'formatter': 'default_formatter',
                "class": "logging.StreamHandler",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            },
            "allInfos":{
                "formatter": "default_formatter",
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "maxBytes": megaBytes * 100,
                "backupCount": 3,
                "filename": os.path.join(basePathLogs, "allInfos.log")
            }
        },
        'loggers': {
            'app': {
                'handlers': ['allInfos', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            'app.test': {
                'handlers': [],
                'level': 'INFO',
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(MY_LOGGING_CONFIG)

def getAppLogger() -> logging.Logger:
    logger = logging.getLogger('app')
    logger.info('Logger config loaded.')
    return logger

def getChildLogger(childName : str) -> logging.Logger:
    return logging.getLogger("app").getChild(childName)