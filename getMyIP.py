# coding:utf-8
import socket


def get_intranet_ip():
    # 获取本机电脑名
    my_name = socket.getfqdn(socket.gethostname())
    # 获取本机ip
    my_intranet_ip = socket.gethostbyname(my_name)
    return my_intranet_ip
