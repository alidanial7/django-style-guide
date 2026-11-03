from config.env import env

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                env(
                    "REDIS_CHANNEL_LAYER_LOCATION",
                    default=env("REDIS_LOCATION", default="redis://localhost:6379/2"),
                )
            ],
        },
    },
}
