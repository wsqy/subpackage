#!/bin/env python2.7
# coding:utf-8

import os
import gevent
import settings
import task
import getMyIP
from copy import deepcopy
from messageNotice import Message
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')

upload_subpackages = []
# upload_subpackages = Queue.Queue(maxsize=0)


class Upload:
    def __init__(self):
        self.no_task_sleep_time = settings.no_task_sleep_time

    def initialize_message(self):
        message = Message()
        return message

    def get_upload_info(self, response):
        for st in settings.storageList:
            # conf = settings.storage_config.get(st)
            conf = deepcopy(settings.storage_config.get(st))
            conf["filename"] = response["filename"]
            conf["packet_dir_path"] = response["packet_dir_path"]
            conf["notice_url"] = response["notice_url"]
            upload_subpackages.append(conf)

    def get_upload_task(self):
        while True:
            if len(upload_subpackages) == 0:
                gevent.sleep(self.no_task_sleep_time)
            else:
                # logger.debug(upload_subpackages)
                upload_subpackage = upload_subpackages.pop()
                self.upload_cloud(upload_subpackage)

    def get_cloud_file_path(self, conf):
        filename = conf.get("filename")
        # apk_base_path = os.path.basename(filename).split("_")[0]
        apk_base_path = conf.get("packet_dir_path")
        cloud_filename = os.path.join(conf.get("basedir", ""), apk_base_path, os.path.basename(filename))
        return cloud_filename

    def get_driver_hand_way(self, conf):
        driver = conf.get("DRIVER")
        upload_module = __import__("UploadFile." + driver, globals(), locals(), [driver])
        h_driver = getattr(upload_module, driver)
        h_driver = h_driver(conf)
        upload_file = getattr(h_driver, "upload_file")
        return upload_file

    def upload_success_handle(self, conf):
        filename = conf.get("filename")
        notice_url = conf.get("notice_url")
        packet_dir_path = conf.get("packet_dir_path")
        response_info = {
            "filename": filename,
            "notice_url": notice_url,
            "packet_dir_path": packet_dir_path,
        }
        # 从任务记录中删除待上传记录
        delete_task = task.get_task_hand_way("delete_task")
        upload_file_schedule_key = settings.upload_file_schedule_key_prefix + ":" + getMyIP.get_intranet_ip()
        delete_task(upload_file_schedule_key, response_info)

        # 上传成功 从唯一性任务集合中删除
        rem_set = task.get_task_hand_way("rem_set")
        rem_set(settings.task_execute_key, filename)

        logger.info("上传子包%s成功,准备删除子包" % filename)
        add_set = task.get_task_hand_way("add_set")
        task_subpackage_set = settings.task_subpackage_set_prefix + ":" + getMyIP.get_intranet_ip()
        add_set(task_subpackage_set, filename)
        logger.debug("塞子包%s完成" % filename)

        logger.info("上传子包%s成功,准备通知%s " % (filename, notice_url))
        # doing 要求通知中新加&filename=xxxxx
        basefilename = os.path.basename(filename)
        new_notice_url = "%s&filename=%s" % (notice_url, basefilename)
        message = self.initialize_message()
        message.finish_message_notice(new_notice_url)

    def upload_cloud(self, conf):
        filename = conf.get("filename")
        cloud_filename = self.get_cloud_file_path(conf)
        # logger.debug(cloud_filename)
        upload_file = self.get_driver_hand_way(conf)
        try:
            has_subfile = os.path.isfile(filename)
            if has_subfile:
                upload_file(cloud_filename, filename)
                # 成功后的通知与删除
                self.upload_success_handle(conf)
                # upload_subpackages.get(filename)[0] -= 1
            else:
                logger.error("子包%s路径不存在....." % filename)
        except Exception, e:
            logger.error(e)
            upload_subpackages.append(conf)
            # upload_subpackages.get(filename)[2].append(conf)
