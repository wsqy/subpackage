#!/usr/bin/env python2.7
# coding:utf-8

import signal
import time
import sys
import task
from gevent import monkey
monkey.patch_all()
import gevent
from setproctitle import setproctitle, getproctitle
import settings
import packet
import getMyIP
from loggingInfoSent import alarm_info_format, sent_log_info
from messageNotice import Message
from subpackageUpload import Upload
from taskRestore import Restore
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

setproctitle('subpackage')


class SubPackage:
    def __init__(self):
        self.retry_packet_count = settings.retry_packet_count
        self.packet_count = settings.packet_count
        self.message_count = settings.message_count
        self.retry_upload_count = settings.retry_upload_count
        self.is_run = True

    def setQuit(self, pid, signal_num):
        self.is_run = False

    def initialize_upload(self):
        upload = Upload()
        return upload

    def initialize_message(self):
        message = Message()
        return message

    def gevent_join(self):
        gevent_task = []
        for each in range(self.packet_count):
            gevent_task.append(gevent.spawn(self.packet))
        for each in range(self.retry_packet_count):
            gevent_task.append(gevent.spawn(self.retry_packet))
        for each in range(self.message_count):
            message = self.initialize_message()
            gevent_task.append(gevent.spawn(message.message_queue()))
        for each in range(self.retry_upload_count):
            upload = self.initialize_upload()
            gevent_task.append(gevent.spawn(upload.get_upload_task))
        gevent.joinall(gevent_task)

    def get_packet_error_time(self, data):
        return data.get("extend").get("packet_timeout", None)

    def packet_error_time_handle(self, data_loads):
        error_time = self.get_packet_error_time(data_loads)
        if (error_time) and time.time() > error_time:
            sent_log_info(alarm_info_format(
                "error", data_loads.get("extend").get("error_key")))

    def subpackage_upload_handle(self, response, data_loads):
        message = response.get_status_key()
        # 任务恢复:  从进度task key里删除 data_loads
        delete_task = task.get_task_hand_way("delete_task")
        delete_task(settings.task_schedule_key, data_loads)
        packet_errorcode = response.get_error_code()
        if packet_errorcode // 100 == 2:
            filename = response.get_filename()
            response.notice_url = data_loads.get("finish_notice_url")
            logger.debug(" 准备上传%s......" % filename)
            res = {
                "filename": response.get_filename(),
                "notice_url": response.notice_url,
                "packet_dir_path": response.get_packet_dir_path()
            }
            #  任务恢复: 把response信息扔到 进度uploadfile key里,这里把class转成了dict方便json转换
            push_task = task.get_task_hand_way("push_task")
            upload_file_schedule_key = settings.upload_file_schedule_key + ":" + getMyIP.get_intranet_ip()
            push_task(upload_file_schedule_key, res)
            upload = self.initialize_upload()
            upload.get_upload_info(res)
        elif packet_errorcode // 100 == 3:
            # TODO 写到单独的文件中
            sent_log_info("%s\t%s" % (response.get_filename(), response.get_status_key()))
        else:
            # 错误的扔进redis, 并检测是否有消息超时时间，如果没有则添加此时间为当前时间的后log_post_time 秒
            error_time = self.get_packet_error_time(data_loads)
            if not error_time:
                data_loads["extend"]["packet_timeout"] = time.time() + settings.log_post_time
            data_loads["extend"]["error_key"] = message
            push_task = task.get_task_hand_way("push_task")
            push_task(settings.task_store_retry_key, data_loads)

    def get_data_info(self, retry=False):
        get_task = task.get_task_hand_way("get_task")
        if retry:
            data_loads = get_task(settings.task_store_key)
        else:
            data_loads = get_task(settings.task_store_retry_key)
        #   任务恢复: 把data_loads信息扔到 进度task key里
        push_task = task.get_task_hand_way("push_task")
        push_task(settings.task_schedule_key, data_loads)
        return data_loads

    def package_task(self, data_loads):
        logger.debug("开始分母包:%s...." % (data_loads.get("filename")))
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
            logger.debug("开始解任务.....")
            # 获取消息的redis ,并解码成python格式
            data_loads = self.get_data_info()
            response = self.package_task(data_loads)
            logger.debug("子包:%s\t状态:%s" % (response.get_filename(), response.get_status_key()))
            self.subpackage_upload_handle(response, data_loads)

    def retry_packet(self):
        while True:
            if not self.is_run:
                # sent_log_info(alarm_info_format("warning", "been kill"))
                break
            data_loads = self.get_data_info(retry=True)
            self.packet_error_time_handle(data_loads)
            response = self.package_task(data_loads)
            logger.debug("子包:%s\t状态:%s" % (response.get_filename(), response.get_status_key()))
            self.subpackage_upload_handle(response, data_loads)


if __name__ == "__main__":
    # with daemon.DaemonContext():
        r = Restore()
        logger.debug("准备恢复任务现场.....")
        r.task_resume()
        logger.debug("任务现场恢复完成，开始接受打包任务.....")
        p = SubPackage()
        signal.signal(signal.SIGHUP, p.setQuit)
        p.gevent_join()
