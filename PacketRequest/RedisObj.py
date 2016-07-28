# coding:utf-8
import time
import json
import redis
from BaseObj import BaseObj
import settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')


class RedisObj(BaseObj):
    def __init__(self):
        self.__redis_host = settings.redis_host
        self.__redis_port = settings.redis_port
        self.__redis_db = settings.redis_db
        self.__redis_auth = settings.redis_auth
        self.redis_sleep_time = settings.no_task_sleep_time

    def object2dict(self, obj):
        # convert object to a dict
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d

    def dict2object(self, d):
        # convert dict to object
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module, class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items())  # get args
            inst = class_(**args)  # create new instance
        else:
            inst = d
        return inst

    def get_redis_pool(self):
        redisHandler = redis.ConnectionPool(host=self.__redis_host,
                           port=self.__redis_port, db=self.__redis_db, password=self.__redis_auth)
        if self.__redis_auth.strip() != '':
            pass

        return redisHandler

    def get_task(self, key):
        redis_pop = redis.Redis(connection_pool=self.get_redis_pool())
        task_info = redis_pop.rpop(key)
        while not task_info:
            time.sleep(self.redis_sleep_time)
            task_info = redis_pop.rpop(key)
        logger.debug("取到一个数据")
        try:
            task_info = json.loads(task_info)
        except TypeError:
            task_info = json.loads(task_info, object_hook=self.dict2object)
        return task_info

    def push_task(self, key, data):
        redis_push = redis.Redis(connection_pool=self.get_redis_pool())
        try:
            data = json.dumps(data)
        except TypeError:
            data = json.dumps(data, default=self.object2dict)
        redis_push.lpush(key, data)

    def delete_task(self, key, data):
        redis_delete = redis.Redis(connection_pool=self.get_redis_pool())
        try:
            data = json.dumps(data)
        except TypeError:
            data = json.dumps(data, default=self.object2dict)
        redis_delete.lrem(key, data, 1)
