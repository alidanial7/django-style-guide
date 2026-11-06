from __future__ import annotations

from abc import ABC, abstractmethod


class SmsProvider(ABC):
    """Strategy interface for delivering OTP / transactional SMS."""

    @abstractmethod
    def send_otp(self, *, phone: str, message: str) -> None:
        """Send ``message`` to a normalized phone (e.g. ``989134543456``)."""
