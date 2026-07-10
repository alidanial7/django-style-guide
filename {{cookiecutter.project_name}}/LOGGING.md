# Logging conventions
#
# Config: config/settings/logging.py (+ config/logging_formatters.py, config/request_id.py)
# Env: DJANGO_LOGGING_LEVEL (uppercased; invalid → INFO), LOG_TO_FILE, LOG_WHEN,
#      LOG_INTERVAL, LOG_BACKUP_COUNT, LOG_SQL
#
# logs/.gitkeep keeps the empty logs/ folder in git; real log files stay ignored (logs/**).
#
# Handlers:
#   console    → human-readable (asctime | level | name | message)
#   app_file   → logs/app/app.log JSON lines, level INFO+ (includes WARNING)
#   error_file → logs/error/error.log JSON lines, level ERROR+
#   sql_console → only when LOG_SQL=true
#
# django.request ERROR+ → console + app_file + error_file (when LOG_TO_FILE), propagate False
#
# request_id:
#   RequestIdMiddleware sets X-Request-ID (inbound or uuid4) on request + response
#   RequestIdFilter attaches it to log records → JSON field "request_id" when present
#
# Use:
#   logger = logging.getLogger(__name__)
#   logger.info("user %s failed", user_id)   # lazy % formatting, not f-strings
#   logger.exception("...")                  # inside except for unexpected errors
# Never log secrets, tokens, or passwords.
