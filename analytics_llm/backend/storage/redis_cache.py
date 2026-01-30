import redis
cache = redis.Redis(host="redis", port=6379)

def get(key):
    return cache.get(key)

def set(key, val, ttl=300):
    cache.setex(key, ttl, val)
