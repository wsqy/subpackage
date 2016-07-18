# coding:utf-8
import time
import json
import redis
from baseObj import baseObj
import settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')

class RedisObj(baseObj):
	def __init__(self):
		self.__redis_host = settings.redis_host
		self.__redis_port = settings.redis_port
		self.__redis_db = settings.redis_db
		self.__redis_auth = settings.redis_auth
		self.redis_key = settings.redis_key
		self.redis_retry_key = settings.redis_retry_key
		self.redis_sleep_time = settings.redis_sleep_time

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
		task_info = json.loads(task_info)
		return task_info

	def push_task(self, key, data):
		redisPush = redis.Redis(connection_pool=self.get_redis_pool())
		logger.debug("失败继续扔进redis")
		data = json.dumps(data)
		redisPush.lpush(key, data)
