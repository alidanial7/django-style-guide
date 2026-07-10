# Validation & error architecture
#
# common = platform only. users = identity/auth domain only.
#
# Boundaries:
#   common/errors      → platform ErrorCode only (required, unique, not_null, …)
#   users/errors       → UserErrorCode only (codes; never raising validators)
#   common/validators  → generic is_* only; see string.py for commented example
#   users/validators   → password.py (is_* pures + *Validator; naming separates them)
#   common/db/integrity → IntegrityError → field-keyed ValidationError / APIException
#   common/http        → API envelope {success, status, result, messages}
#     success: api_response(...)  → result = payload, messages = {}
#     error:   api_exception_handler → result = [], messages.<field> = [{message, code}, ...]
#     fallback error code: invalid
#
# Messages: use gettext_lazy / _() with lowercase msgids; parameterized
# ValidationError messages use params={...} (do not pre-format with %).
#
# Password validators:
#   API / DRF input uses users.validators.PASSWORD_VALIDATORS.
#   Django AUTH_PASSWORD_VALIDATORS includes the same domain rules via
#   Password*DjangoValidator adapters (plus Django built-ins). Keep both in sync
#   when changing password policy.
#
# Write paths: common.services.model_create/model_save, or
#   except IntegrityError: map_integrity_error(...)  (e.g. users.services.create_user)
#
# Adding a new field rule:
# 1. If the check is generic across apps → pure is_* in common/validators/
#    If it is domain-specific (e.g. password) → pure is_* in <app>/validators/
# 2. Add domain ErrorCode in <app>/errors/codes.py (not common)
# 3. Add @deconstructible raising validator in <app>/validators/ (Django ValidationError)
# 4. Attach on model field when universal; reuse on serializer fields
# 5. For uniqueness/FK/NOT NULL: DB constraint + common/db/integrity mapping
