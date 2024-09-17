from django.core.cache import cache

def delete_cache(keys: list):
    for key in keys:
        cache.delete(key)
