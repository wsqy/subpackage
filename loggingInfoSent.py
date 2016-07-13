# coding:utf-8
import time
import socket

import settings


def alarm_info_format(level, Info):
    return "%s\t%s\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), level, Info)


def sent_log_info(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPTarget = (settings.UDP_HOST, settings.UDP_PORT)
    print "发送日志"
    s.sendto(data, UDPTarget)
    s.close()