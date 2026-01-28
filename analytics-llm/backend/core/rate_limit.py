import redis
r = redis.Redis(host="redis", port=6379)

def allow_request(key, limit=100):
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    return count <= limit
