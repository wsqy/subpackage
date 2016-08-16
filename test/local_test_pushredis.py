# coding:utf-8
import redis
import json
import os
data = {
    'filename': '2',
    'channel_id': 1,
    'extend': {
        'channel_version': '0.7',
        'enforcement': False,
    },
    'finish_notice_url': 'http://192.168.5.20/test2.php',
}
# , password="uid"
redis_pool = redis.ConnectionPool(host='121.199.34.235', port=6379, db=0, password="uid")
r = redis.Redis(connection_pool=redis_pool)
redis_key = "6y:apk:subpackage:task"
print r.lpush(redis_key, json.dumps(data))

# print(r.llen(redis_key))
# print(r.llen("6y:apk:subpackage:task:schedule:task"))
# print(r.llen("6y:apk:subpackage:task:schedule:uploadfile"))
# print(r.lrange("6y:apk:subpackage:task:schedule:task", 0, 1))
# print(r.lrange("6y:apk:subpackage:task:schedule:uploadfile", 0, 2))
# print(r.lrem("6y:apk:subpackage:task:schedule:task", data, 2))
# print r.rpop("6y:apk:subpackage:task:schedule:task")
# print r.rpop("6y:apk:subpackage:task:schedule:uploadfile")
# print(r.llen("task_store_retry_key"))
# print r.srem("tset_set", json.dumps(data))


