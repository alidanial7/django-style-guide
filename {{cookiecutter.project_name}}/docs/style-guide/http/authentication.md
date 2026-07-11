# 🔑 Authentication

{%- if cookiecutter.use_jwt == "y" %}
> This project was generated with **JWT** (`djangorestframework-simplejwt` + refresh token blacklist).
{%- else %}
> This project was generated with **session** authentication (cookie-based).
{%- endif %}
>
> The `users` app always ships register, profile, and password flows. Auth mechanism is chosen at cookiecutter generation time — do not mix both stacks casually.

---

## 🎯 Big picture

```mermaid
flowchart TB
    subgraph Public["Public (no ApiAuthMixin)"]
        REG[Register]
        LOGIN[Login]
        RESET[Password reset]
    end
    subgraph Protected["Protected (ApiAuthMixin)"]
        PROF[Profile GET/PATCH]
        CHG[Password change]
{%- if cookiecutter.use_jwt != "y" %}
        SOUT[Session logout]
{%- endif %}
    end
{%- if cookiecutter.use_jwt == "y" %}
    LOGIN -->|access + refresh| CLIENT[Client stores tokens]
    CLIENT -->|Authorization: Bearer access| PROF
    CLIENT -->|refresh body| REF[Refresh — rotates tokens]
{%- else %}
    LOGIN -->|Set-Cookie sessionid| CLIENT[Browser / client]
    CLIENT -->|cookie + CSRF on unsafe methods| PROF
{%- endif %}
```

| Concern | Location |
|---------|----------|
| Login / logout / JWT or session views | `users/apis/auth/` |
| Password change / reset | `auth_password_apis.py` + `user_services` |
| Register | `users/apis/users/register/` |
| Profile | `users/apis/users/profile/` |
| URLConf | `users/urls/auth.py`, `users/urls/users.py` |
| User model | `users.BaseUser` (`AUTH_USER_MODEL`) |
| DRF default auth class | `config/settings/drf.py` |
| Permissions mixin | [Permissions](permissions.md) |

---

{%- if cookiecutter.use_jwt == "y" %}
## 🪙 JWT flow

### Login

`POST /api/v1/auth/jwt/login/` with `email` + `password` (SimpleJWT obtain pair; field names follow SimpleJWT — typically `email` as username field via custom user).

Response is wrapped in the [API envelope](api-envelope.md); `result` contains `access` and `refresh`.

```http
Authorization: Bearer <access>
```

Views wrap SimpleJWT and re-envelope. Login uses `AuthJwtTokenObtainSerializer` (field name follows `USERNAME_FIELD` = `email`) and documents the success envelope via `envelope_serializer`.

```python
# users/apis/auth/auth_jwt_apis.py
class AuthJwtLoginApi(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, http_status=response.status_code)
```

### Refresh (rotation + blacklist)

Configured in `config/settings/jwt.py`:

```python
SIMPLE_JWT = {
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    ...
}
```

On every successful `POST /api/v1/auth/jwt/refresh/`:

1. Client sends the current `refresh`  
2. Server returns a **new** `access` and a **new** `refresh`  
3. The **previous** refresh token is blacklisted and must not be reused  

Clients must **replace** stored refresh tokens after each refresh. Reusing an old refresh → error.

### Verify

`POST /api/v1/auth/jwt/verify/` — checks whether a token is valid (throttled). Useful for gateways/clients; not a substitute for sending Bearer on each API call.

### Logout

`POST /api/v1/auth/jwt/logout/` with body `{ "refresh": "<token>" }`:

- Public (no access token required) — possession of the refresh token is enough to blacklist it  
- Service `logout(refresh_token=...)` blacklists via SimpleJWT; invalid/expired → `UserErrorCode.INVALID_TOKEN`  

```python
# AuthLogoutApi → logout(refresh_token=...)
return api_response(data={"detail": "logged out."})
```

Access tokens remain valid until they expire (stateless). For immediate access revocation you would need a short access lifetime and/or an allowlist — not shipped by default.

### Lifetimes (env-configurable)

| Token | Default | Env variable |
|-------|---------|--------------|
| Access | 15 minutes | `JWT_ACCESS_TOKEN_LIFETIME_SECONDS` |
| Refresh | 7 days | `JWT_REFRESH_TOKEN_LIFETIME_SECONDS` |

After enabling JWT / upgrading, run migrations so **token blacklist** tables exist:

```bash
python manage.py migrate
```

### Register + tokens

`POST /api/v1/users/register/` is public (throttled `register`). Output serializer includes JWT `token.refresh` / `token.access` so the client can authenticate immediately without a separate login call.

### Endpoint map (JWT)

| Endpoint | Auth | Notes |
|----------|------|-------|
| `POST /api/v1/auth/jwt/login/` | public | throttle `auth` |
| `POST /api/v1/auth/jwt/refresh/` | public | throttle `auth`; rotates refresh |
| `POST /api/v1/auth/jwt/verify/` | public | throttle `auth` |
| `POST /api/v1/auth/jwt/logout/` | public | blacklists refresh |
| `POST /api/v1/auth/password/change/` | JWT (`ApiAuthMixin`) | current + new password |
| `POST /api/v1/auth/password/reset/` | public | throttle `password_reset` |
| `POST /api/v1/auth/password/reset/confirm/` | public | throttle `password_reset` |
| `POST /api/v1/users/register/` | public | throttle `register`; returns tokens |
| `GET` / `PATCH /api/v1/users/profile/` | JWT | current user |

{%- else %}
## 🍪 Session flow

### Login

`POST /api/v1/auth/session/login/` with `email` + `password`.

On success Django `login(request, user)` sets the **session cookie**. Response envelope includes `{ "email": ... }`.

Invalid credentials → validation-style error with `ErrorCode.INVALID` (no user enumeration beyond generic failure message).

### Logout

`POST /api/v1/auth/session/logout/` — **authenticated** (`ApiAuthMixin`). Calls Django `logout(request)`.

### CSRF (required for browsers)

Unsafe methods with session cookies need a valid CSRF token (`X-CSRFToken` or form field). See [Permissions](permissions.md).

`LOGIN_URL` is set to the session login API path in `config/settings/auth.py` for Django’s login redirect helpers.

### Register

`POST /api/v1/users/register/` creates the user and **logs them in** (session) in the same request when session auth is selected.

### Endpoint map (session)

| Endpoint | Auth | Notes |
|----------|------|-------|
| `POST /api/v1/auth/session/login/` | public | throttle `auth` |
| `POST /api/v1/auth/session/logout/` | session | `ApiAuthMixin` |
| `POST /api/v1/auth/password/change/` | session | `ApiAuthMixin` |
| `POST /api/v1/auth/password/reset/` | public | throttle `password_reset` |
| `POST /api/v1/auth/password/reset/confirm/` | public | throttle `password_reset` |
| `POST /api/v1/users/register/` | public | creates user + session login |
| `GET` / `PATCH /api/v1/users/profile/` | session | `ApiAuthMixin` |

{%- endif %}

---

## 🔒 Password change & reset

Shared for both auth modes; implemented in `auth_password_apis.py` + `user_services`.

### Change (authenticated)

`POST /api/v1/auth/password/change/` — requires `ApiAuthMixin`.

Body: current password + new password (+ confirm as defined by serializer). Wrong current password → `UserErrorCode.PASSWORD_INCORRECT`. New password uses the same domain [password validators](validation-and-errors.md).

### Reset request (public)

`POST /api/v1/auth/password/reset/` with `{ "email": "…" }`.

| Behavior | Why |
|----------|-----|
| Always returns success-style message | Avoid account enumeration |
| Email sent only if user exists | `request_password_reset` in services |
| Console email backend locally | `EMAIL_*` in `.env` |

Email content includes `uid`, `token`, and a link built with `APP_DOMAIN` (frontend reset URL). Locally you read the console backend output.

### Reset confirm (public)

`POST /api/v1/auth/password/reset/confirm/` with `uid`, `token`, `new_password`, `confirm_password`.

Invalid/expired token → `UserErrorCode.INVALID_RESET_TOKEN`.

Throttles: scope `password_reset` (see [Throttling](throttling.md)).

---

## 👤 Profile & user model

| Piece | Detail |
|-------|--------|
| User model | `users.BaseUser` — email as `USERNAME_FIELD`, no username |
| Profile | `bio`, `avatar`; created by [signal](../layers/signals.md) on user create |
| Default avatar | Static `users/default_avatar.png` via selector |
| Update | `PATCH /api/v1/users/profile/` — multipart for avatar |

Password policy for admin/`set_password` is wired in `AUTH_PASSWORD_VALIDATORS` (`config/settings/auth.py`) including domain `Password*DjangoValidator` adapters — keep in sync with API `PASSWORD_VALIDATORS`.

---

## 🚫 Not included by design

These are intentionally **out of scope** for the template:

| Feature | Guidance |
|---------|----------|
| Email verification | Add before issuing tokens / activating accounts if your product needs it |
| Social login | Integrate a provider package in the product layer |
| 2FA / MFA | Add after basic auth is stable |

Do not pretend they exist in clients or docs for a fresh project.

---

## 🧪 Client integration checklist

{%- if cookiecutter.use_jwt == "y" %}
1. Register or login → store `access` + `refresh`  
2. Send `Authorization: Bearer <access>` on protected routes  
3. On 401, refresh once → replace both tokens → retry  
4. On logout, send refresh to blacklist endpoint and clear local storage  
5. Never log tokens; never put them in URL query strings  
{%- else %}
1. Login or register → persist session cookie  
2. Ensure CSRF token on `POST`/`PATCH`/`PUT`/`DELETE`  
3. Logout via authenticated session logout endpoint  
4. Same-site / CORS settings must allow credentialed requests from your frontend origin  
{%- endif %}

---

## ❌ Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
{%- if cookiecutter.use_jwt == "y" %}
| Reusing an old refresh after rotation | Always save the new refresh |
| Sending refresh as Bearer access | Access in `Authorization`; refresh in refresh/logout body |
| Long-lived access tokens “for convenience” | Keep access short; use refresh |
{%- else %}
| Forgetting CSRF on SPA POSTs | Wire CSRF header from cookie |
| Storing passwords in localStorage | Session cookie + HTTPS |
{%- endif %}
| Building auth views outside `users/apis/auth/` | Keep identity in the users domain |
| Skipping throttle on login/register | Use scoped rates from settings |

---

## 🔗 Related docs

| Doc | Why |
|-----|-----|
| [Permissions](permissions.md) | `ApiAuthMixin` and custom gates |
| [Validation & errors](validation-and-errors.md) | Password codes / validators |
| [APIs](../layers/apis.md) | View patterns |
| [Throttling](throttling.md) | `auth` / `register` / `password_reset` |
| [Swagger](swagger.md) | Trying endpoints in DEBUG |
| [URLs](../layers/urls.md) | Path map |
