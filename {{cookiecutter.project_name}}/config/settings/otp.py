from config.env import env

# When True, OTP codes are always OTP_TEST_CODE and SMS is not sent.
OTP_TEST = env.bool("OTP_TEST", default=False)
OTP_TEST_CODE = "12345"

OTP_CODE_LENGTH = env.int("OTP_CODE_LENGTH", default=5)
OTP_TTL_SECONDS = env.int("OTP_TTL_SECONDS", default=120)
OTP_RESEND_SECONDS = env.int("OTP_RESEND_SECONDS", default=60)
OTP_MAX_ATTEMPTS = env.int("OTP_MAX_ATTEMPTS", default=5)

# Strategy key → users.providers.sms registry (default stub is empty for you to fill).
SMS_PROVIDER = env("SMS_PROVIDER", default="stub")
