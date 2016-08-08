# coding:utf-8
import settings
import task
import gevent
from subpackageUpload import Upload
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')


class Restore:
    def __init__(self):
        self.retry_upload_count = settings.retry_upload_count

    def initialize_upload(self):
        upload = Upload()
        return upload

    def gevent_join(self):
        gevent_task = []
        for each in range(self.retry_upload_count):
            upload = self.initialize_upload()
            gevent_task.append(gevent.spawn(upload.get_upload_task))
        gevent.joinall(gevent_task)

    def delete_task_set(self):
        del_key = task.get_task_hand_way("del_key")
        del_key(settings.task_execute_key)
        logger.debug("唯一性任务的集合删除完成...")

    def task_resume_upload(self, key=settings.upload_file_schedule_key):
        get_task_count = task.get_task_hand_way("get_task_count")
        upload_task_count = get_task_count(key)
        if upload_task_count:
            get_task = task.get_task_hand_way("get_task")
            self.gevent_join()
            for count in range(upload_task_count):
                up_file = get_task(key)
                logger.debug(up_file)
                upload = self.initialize_upload()
                upload.get_upload_info(up_file)
        else:
            logger.debug("没有待上传的子包.......")

    def task_resume_subpackage(self, key_source=settings.task_schedule_key, key_target=settings.task_store_key):
        get_task_count = task.get_task_hand_way("get_task_count")
        upload_task_count = get_task_count(key_source)
        if upload_task_count:
            get_task = task.get_task_hand_way("get_task")
            push_task = task.get_task_hand_way("push_task")
            for count in range(upload_task_count):
                tasks = get_task(key_source)
                push_task(key_target, tasks, reverse=True)
        else:
            logger.debug("没有待恢复的任务.......")

    def task_resume(self):
        logger.debug("准备删除唯一性任务的集合...")
        self.delete_task_set()
        logger.debug("准备恢复子包上传...")
        self.task_resume_upload()
        logger.debug("准备恢复打包任务...")
        self.task_resume_subpackage()
