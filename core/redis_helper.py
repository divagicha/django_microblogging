from django.core.cache import cache


class RedisInterface:
    @staticmethod
    def set_redis_val(key, value, ttl=None):
        cache.set(key, value, ttl)

    @staticmethod
    def get_redis_val(key):
        return cache.get(key)

    @staticmethod
    def delete_redis_key(key):
        return cache.delete(key)
