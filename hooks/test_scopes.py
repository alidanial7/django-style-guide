#!/usr/bin/env python3
"""Unit checks for API scope parsing."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scopes import parse_api_scopes, scope_pascal, validate_api_scopes  # noqa: E402


class ScopeTests(unittest.TestCase):
    def test_parse_dedupes_and_lowercases(self) -> None:
        self.assertEqual(
            parse_api_scopes(" Admin, factory,admin , customer "),
            ["admin", "factory", "customer"],
        )

    def test_rejects_spaces_and_reserved(self) -> None:
        with self.assertRaises(ValueError):
            validate_api_scopes(["content team"])
        with self.assertRaises(ValueError):
            validate_api_scopes(["health"])
        with self.assertRaises(ValueError):
            validate_api_scopes([])

    def test_pascal(self) -> None:
        self.assertEqual(scope_pascal("admin"), "Admin")
        self.assertEqual(scope_pascal("content_team"), "ContentTeam")


if __name__ == "__main__":
    unittest.main()
