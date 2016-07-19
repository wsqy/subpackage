#!/bin/env python2.7
# coding:utf-8

import signal
import time
import urllib2
import os
from gevent import monkey
monkey.patch_all()
import gevent
from setproctitle import setproctitle,getproctitle

import settings
import packet
from loggingInfoSent import alarm_info_format, sent_log_info
from message_notice import Message
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

setproctitle('subpackage')


class SubPackage:
    def __init__(self):
        self.retry_packet_num = settings.retry_packet_num
        self.packet_num = settings.packet_num
        self.message_num = settings.message_num
        self.retry_upload_num = settings.retry_upload_num
        self.message = Message()
        self.upload_subpackage_dict = {}
        self.is_run = True

    def setQuit(self, pid, signal_num):
        self.is_run = False

    def gevent_join(self):
        gevent_task = [] 
        for each in range(self.packet_num):
            gevent_task.append(gevent.spawn(self.packet)) 
        for each in range(self.retry_packet_num):
            gevent_task.append(gevent.spawn(self.retry_packet)) 
        for each in range(self.message_num):
            gevent_task.append(gevent.spawn(self.message.message_queue()))
        for each in range(self.retry_upload_num):
            gevent_task.append(gevent.spawn(self.get_upload_task))
        gevent.joinall(gevent_task)


    def get_packet_error_time(self, data):
        return data.get("extend").get("packet_timeout", None)

    def get_task_hand_way(self, access_way):
        task_type = settings.task_type.capitalize() + "Obj"
        upload_module = __import__("PacketRequest." + task_type)
        up_access = getattr(getattr(upload_module, task_type), task_type)
        return getattr(up_access(), access_way)

    def subpackage_upload_handle(self, response, data_loads):
        message = response.get_status_key()
        if message == "COMPLETE" or message == "HAVEN_SUB":
            filename = response.get_filename()
            finish_url = data_loads.get("finish_notice_url")
            logger.debug(" 准备上传%s。。。。。。" % filename)
            self.get_upload_info(response, finish_url)
        else:
            # 错误的扔进redis, 并检测是否有消息超时时间，如果没有则添加此时间为当前时间的后log_post_time 秒
            error_time = self.get_packet_error_time(data_loads)
            if not error_time:
                data_loads["extend"]["packet_timeout"] = time.time() + settings.log_post_time
            data_loads["extend"]["error_key"] = message
            push_task = self.get_task_hand_way("push_task")
            push_task(settings.task_store_retry_key, data_loads)

    def get_upload_info(self, response, notice_url):
        filename = response.get_filename()
        self.upload_subpackage_dict[filename] = [len(settings.storageList), notice_url, []]
        for st in settings.storageList:
            conf = settings.storage_config.get(st)
            conf["filename"] = filename
            conf["packet_dir_path"] = response.get_packet_dir_path()
            self.upload_subpackage_dict.get(filename)[2].append(conf)

    def get_upload_task(self):
        while True:
            if len(self.upload_subpackage_dict) == 0:
                gevent.sleep(2)
            else:
                k, v = self.upload_subpackage_dict.popitem()
                if v[0] == 0:
                    # 全部上传成功，做一个通知 url = v[1]
                    logger.info("上传成功,删除子包")
                    os.remove(k)
                    self.message.finish_message_notice(v[1])
                    continue
                else:
                    conf = v[2].pop()
                    v[0] -= 1
                    self.upload_subpackage_dict[k] = v
                    self.upload_cloud(conf)

    def get_cloud_file_path(self, conf):
        filename = conf.get("filename")
        # apk_base_path = os.path.basename(filename).split("_")[0]
        apk_base_path = conf.get("packet_dir_path")
        cloud_filename = os.path.join(conf.get("basedir", ""), apk_base_path, os.path.basename(filename))
        return cloud_filename

    def get_driver_hand_way(self, conf, upload_file):
        driver = conf.get("DRIVER")
        upload_module = __import__("UploadFile." + driver)
        up_driver = getattr(getattr(upload_module, driver), driver)
        h_driver = up_driver(conf)
        upload_file = getattr(h_driver, "upload_file")
        return upload_file

    def upload_cloud(self, conf):
        filename = conf.get("filename")
        cloud_filename = self.get_cloud_file_path(conf)
        logger.debug(cloud_filename)
        upload_file = self.get_driver_hand_way(conf, "upload_file")
        try:
            upload_file(cloud_filename, filename)
        except Exception, e:
            logger.error(e, filename, "失败重传--------")
            # 将文件名封装进这个字典
            self.upload_subpackage_dict.get(filename)[0] += 1
            self.upload_subpackage_dict.get(filename)[2].append(conf)

    def get_data_info(self, retry=False):
        get_task = self.get_task_hand_way("get_task")
        if retry:
            data_loads = get_task(settings.task_store_key)
        else:
            data_loads = get_task(settings.task_store_retry_key)
        return data_loads

    def package_task(self, data_loads):
        logger.debug("开始分包。。。。")
        startTime = time.time()
        response = packet.subpackage(filename=data_loads.get("filename"),
                                     channel_id=data_loads.get("channel_id"),
                                     extend=data_loads.get("extend"),
                                     )
        endTime = time.time()
        spendTime = endTime - startTime
        logger.debug("subpackage spent %f second." % spendTime)
        return response

    def packet(self):
        while True:
            if not self.is_run:
                # sent_log_info(alarm_info_format("warning", "been kill")) 
                break
            logger.debug("开始解任务。。。。。")
            # 获取消息的redis ,并解码成python格式
            data_loads = self.get_data_info()
            response = self.package_task(data_loads)
            logger.debug(response.get_status_key())
            self.subpackage_upload_handle(response, data_loads)

    def packet_error_time_handle(self, data_loads):
        error_time = self.get_packet_error_time(data_loads)
        if (error_time) and time.time() > error_time:
            sent_log_info(alarm_info_format(
                "error", data_loads.get("extend").get("error_key")))

    def retry_packet(self):
        while True:
            if not self.is_run:
                # sent_log_info(alarm_info_format("warning", "been kill"))
                break
            data_loads = self.get_data_info(retry=True)
            self.packet_error_time_handle(data_loads)
            response = self.package_task(data_loads)
            logger.debug(response.get_status_key())
            self.subpackage_upload_handle(response, data_loads)


if __name__ == "__main__":
    # with daemon.DaemonContext():
        p = SubPackage()
        signal.signal(signal.SIGHUP, p.setQuit)
        p.gevent_join()
