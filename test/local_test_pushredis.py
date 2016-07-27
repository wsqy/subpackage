# coding:utf-8
import redis
import json
data = {
    'filename': '2',
    'channel_id': 11,
    'extend': {
        'channel_version': '0.7',
    },
    'finish_notice_url': 'http://192.168.5.20/test3.php',
}
# , password="uid"
redis_pool = redis.ConnectionPool(host='121.199.34.235', port=6379, db=0)
r = redis.Redis(connection_pool=redis_pool)
redis_key = "6y:apk:subpackage:task"
print r.lpush(redis_key, json.dumps(data))

# print r.rpop("greet")

# print(r.lpush("greet", data))
# print(r.llen("greet"))
# print(r.lrange("greet",0,1))
# print(r.lrem("greet", data, 1))
