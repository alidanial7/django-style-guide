#!/usr/bin/env python3
"""Unit checks for inplace target validation / flatten helpers."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from interactive_prompts import (  # noqa: E402
    assert_inplace_target_ok,
    flatten_generated_project,
    list_non_git_entries,
)


class InplaceTargetTests(unittest.TestCase):
    def test_empty_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            assert_inplace_target_ok(Path(tmp))
            self.assertEqual(list_non_git_entries(Path(tmp)), [])

    def test_git_only_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
            (root / ".gitattributes").write_text("* text=auto\n", encoding="utf-8")
            assert_inplace_target_ok(root)

    def test_non_git_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "README.md").write_text("hi\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                assert_inplace_target_ok(root)
            self.assertIn("README.md", str(ctx.exception))

    def test_flatten_moves_and_replaces_gitignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".gitignore").write_text("old\n", encoding="utf-8")

            generated = root / "Demo"
            generated.mkdir()
            (generated / ".gitignore").write_text("new\n", encoding="utf-8")
            (generated / "README.md").write_text("app\n", encoding="utf-8")
            (generated / "pkg").mkdir()
            (generated / "pkg" / "x.py").write_text("x=1\n", encoding="utf-8")

            flatten_generated_project(root, "Demo")

            self.assertFalse(generated.exists())
            self.assertTrue((root / ".git").is_dir())
            self.assertEqual((root / ".gitignore").read_text(encoding="utf-8"), "new\n")
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "app\n")
            self.assertTrue((root / "pkg" / "x.py").is_file())


if __name__ == "__main__":
    unittest.main()
