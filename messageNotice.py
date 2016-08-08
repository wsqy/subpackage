#!/bin/env python2.7
# coding:utf-8
import settings
import urllib2
import gevent
from loggingInfoSent import alarm_info_format, sent_log_info
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')


class Message:
    def __init__(self):
        self.no_task_sleep_time = settings.no_task_sleep_time
        self.message_list = []

    def finish_message_notice(self, Info_url):
        if settings.debug:
            logger.debug("任务完成。。。。")
            return
        try:
            response = urllib2.urlopen(Info_url).read()
            if "success" in response:
                # 打个成功的日志
                logger.debug("消息发送成功")
                logger.debug("上传成功删除文件")
            elif "miss" in response:
                sent_log_info(alarm_info_format("notice", "missing"))
                logger.debug("miss")
            else:
                self.message_list.append(Info_url)
                logger.debug("other")
        except:
            logger.debug("url不可达")
            self.message_list.append(Info_url)

    def message_queue(self):
        # 如果通知队列中有消息则发送消息
        if len(self.message_list) == 0:
            gevent.sleep(self.no_task_sleep_time)
        else:
            post_data = self.message_list.pop()
            self.finish_message_notice(post_data)
