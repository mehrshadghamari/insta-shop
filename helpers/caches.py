import json
from abc import ABC
from abc import abstractmethod

import redis
from django.core.cache import cache
from django.core.cache import cache as django_cache
from pymemcache.client.base import Client as MemcacheClient

from apps.shop.models import Post


# Strategy Interface
class CacheStrategy(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value, timeout=None):
        pass


# Redis Strategy
class RedisCacheStrategy(CacheStrategy):
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def get(self, key):
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key, value, timeout=None):
        self.client.setex(key, timeout or 0, json.dumps(value))


# Memcached Strategy
class MemcachedStrategy(CacheStrategy):
    def __init__(self, host="localhost", port=11211):
        self.client = MemcacheClient((host, port))

    def get(self, key):
        value = self.client.get(key)
        return json.loads(value.decode("utf-8")) if value else None

    def set(self, key, value, timeout=None):
        self.client.set(key, json.dumps(value).encode("utf-8"), expire=timeout)


# Django Cache Strategy
class DjangoCacheStrategy(CacheStrategy):
    def get(self, key):
        return django_cache.get(key)

    def set(self, key, value, timeout=None):
        django_cache.set(key, value, timeout)


# Context Class
class CacheHandler:
    def __init__(self, strategy: CacheStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: CacheStrategy):
        self._strategy = strategy

    def get(self, key):
        return self._strategy.get(key)

    def set(self, key, value, timeout=None):
        self._strategy.set(key, value, timeout)


def clear_related_post_cache(instance, cache_handler):
    post_ids = set()
    shop_ids = set()

    if hasattr(instance, "post_id"):
        post_ids.add(instance.post_id)
        shop_id = getattr(instance, "shop_id", None) or getattr(instance.post, "shop_id", None)
        if shop_id:
            shop_ids.add(shop_id)

    elif hasattr(instance, "content_object"):
        content_object = instance.content_object
        if isinstance(content_object, Post):
            post_ids.add(content_object.id)
            shop_ids.add(content_object.shop_id)

    elif hasattr(instance, "product"):
        post_id = getattr(instance.product, "post_id", None)
        shop_id = getattr(instance.product.post, "shop_id", None)
        post_ids.add(post_id)
        shop_ids.add(shop_id)

    elif hasattr(instance, "option_type") and hasattr(instance.option_type, "product"):
        product = instance.option_type.product
        if hasattr(product, "post"):
            post = product.post
            post_ids.add(post.id)
            if hasattr(post, "shop_id"):
                shop_ids.add(post.shop_id)

    for post_id in post_ids:
        cache_handler.delete(f"post_detail_{post_id}")
    for shop_id in shop_ids:
        cache_handler.delete(f"post_list_{shop_id}")


cache_handler = CacheHandler(DjangoCacheStrategy())
