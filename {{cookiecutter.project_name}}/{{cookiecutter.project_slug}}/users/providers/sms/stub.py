from __future__ import annotations

from {{cookiecutter.project_slug}}.users.providers.sms.base import SmsProvider


class StubSmsProvider(SmsProvider):
    """
    Empty SMS provider — replace the body of ``send_otp`` with your gateway.

    Examples: Kavenegar, Melipayamak, Twilio, Ghasedak, …

    ``phone`` is always stored/normalized as digits with country code and no ``+``
    (Iran mobile example: ``989134543456``).
    """

    def send_otp(self, *, phone: str, message: str) -> None:
        # TODO: wire your SMS provider here.
        # Do not raise — local/dev may run with OTP_TEST=true instead.
        _ = (phone, message)
