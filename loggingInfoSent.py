# coding:utf-8
import time
import socket

import settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')


def alarm_info_format(level, Info):
    return "%s\t%s\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), level, Info)


def sent_log_info(data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPTarget = (settings.UDP_HOST, settings.UDP_PORT)
        logger.debug("发送日志")
        s.sendto(data, UDPTarget)
        s.close()
    except Exception, e:
        logger.error("日志发送失败:%s" % e)
