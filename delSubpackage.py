#!/usr/bin/env python2.7
# coding:utf-8
import redis
import json
import os
import time
task_subpackage_set = "6y:apk:subpackage:subpackages:set"
sleep_time = 10


class RedisObj:
    def __init__(self):
        self.__redis_host = '121.199.34.235'
        self.__redis_port = 6379
        self.__redis_db = 0
        self.__redis_auth = "uid"

    def get_redis_pool(self):
        redis_handler = redis.ConnectionPool(host=self.__redis_host,
                           port=self.__redis_port, db=self.__redis_db, password=self.__redis_auth)
        return redis_handler

    def rem_set(self, key, data):
        redis_con = redis.Redis(connection_pool=self.get_redis_pool())
        data = json.dumps(data)
        return redis_con.srem(key, data)

    def random_member(self, key):
        redis_con = redis.Redis(connection_pool=self.get_redis_pool())
        task_info = redis_con.srandmember(key)
        task_info = json.loads(task_info)
        return task_info


while True:
    try:
        rad_num = RedisObj().random_member(task_subpackage_set)
        if not rad_num:
            print("no data,sleep %s s....." % sleep_time)
            time.sleep(sleep_time)
            continue
        print("get apk : %s" % rad_num)
        os.remove(rad_num)
        rem_set = RedisObj().rem_set(task_subpackage_set, rad_num)
    except TypeError as e:
        print("sleep %s s....." % sleep_time)
        time.sleep(sleep_time)
        continue
