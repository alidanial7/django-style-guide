from config.env import env

# Never ship a production secret as a code default. Local `.env` / `.env.example`
# provide a disposable key for development only.
SECRET_KEY = env("SECRET_KEY")

# Prefer False in shared settings; local.py turns DEBUG on explicitly.
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
