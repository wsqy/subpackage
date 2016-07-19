# coding:utf-8
import os
import logging.config

logging_directory_path = 'log'

def logging_file_path(filename):
    return os.path.join(logging_directory_path, filename)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'notes': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('all.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
        'scripts': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('scripts.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('error.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'loggers': {
        # 定义了一个logger
        'mylogger': {
            'level': 'DEBUG',
            'handlers': ['console', 'notes', 'scripts', 'errors'],
            'propagate': True
        }
    }
}
if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger('mylogger')
    logger.debug('debug1')
    logger.info('info1')
    logger.error('error1')