# coding:utf-8
import redis
import json
data = {
    'filename': 'boyusihailongwang',
    'channel_id': 11,
    'extend': {
        'channel_version': '1.07',
    },
    'finish_notice_url': 'http://192.168.5.20/test3.php',
}
# , password="uid"
redis_pool =  redis.ConnectionPool(host='2cdd06c0eba54c30.m.cnhza.kvstore.aliyuncs.com', port=6379, db=0, password="nhuWq6vgsEypdZF")
r = redis.Redis(connection_pool=redis_pool)
redis_key = "6y:apk:subpackage:task"
print r.lpush(redis_key, json.dumps(data))

# print r.rpop(redis_key)
