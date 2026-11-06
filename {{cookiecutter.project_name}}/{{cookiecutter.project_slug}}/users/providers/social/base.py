from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class SocialIdentity(TypedDict):
    """Normalized identity from a verified provider id_token."""

    provider: str
    subject: str
    email: str
    email_verified: bool


class SocialProvider(ABC):
    """Strategy: verify a provider ID token and return a normalized identity."""

    name: str

    @abstractmethod
    def verify_id_token(self, *, id_token: str) -> SocialIdentity:
        """Validate ``id_token`` and return provider subject + email."""
