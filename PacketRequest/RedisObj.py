# coding:utf-8
import time
import json
import redis

from baseObj import baseObj
import settings

class RedisObj:
    def __init__(self):
        self.__redis_host = settings.redis_host
        self.__redis_port = settings.redis_port
        self.__redis_db = settings.redis_db
        self.__redis_password = settings.redis_password
        self.redis_key = settings.redis_key
        self.redis_retry_key = settings.redis_retry_key
        self.redis_sleep_time = settings.redis_sleep_time

    def get_redis_pool(self):
        return redis.ConnectionPool(host=self.__redis_host,
                                    port=self.__redis_port, db=self.__redis_db)

    def get_task(self, key):
        redis_pop = redis.Redis(connection_pool=self.get_redis_pool())
        task_info = redis_pop.rpop(key)
        while not task_info:
            time.sleep(self.redis_sleep_time)
            task_info = redis_pop.rpop(key)
        print "取到一个数据"
        task_info = json.loads(task_info)
        return task_info

    def push_task(self, key, data):
        redisPush = redis.Redis(connection_pool=self.get_redis_pool())
        print "失败继续扔进redis"
        data = json.dumps(data)
        redisPush.lpush(key, data)
