from config.env import env

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_LOCATION', default='redis://localhost:6379'),
    }
}

CACHE_TTL = 60 * 15
