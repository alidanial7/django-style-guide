import datetime

from config.env import env

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html

JWT_ACCESS_TOKEN_LIFETIME_SECONDS = env.int(
    "JWT_ACCESS_TOKEN_LIFETIME_SECONDS",
    default=60 * 15,
)
JWT_REFRESH_TOKEN_LIFETIME_SECONDS = env.int(
    "JWT_REFRESH_TOKEN_LIFETIME_SECONDS",
    default=60 * 60 * 24 * 7,
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(seconds=JWT_ACCESS_TOKEN_LIFETIME_SECONDS),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(seconds=JWT_REFRESH_TOKEN_LIFETIME_SECONDS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
