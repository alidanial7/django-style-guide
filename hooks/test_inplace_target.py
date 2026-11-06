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
    clean_inplace_target,
    flatten_generated_project,
    is_cookiecutter_template_root,
    list_non_git_entries,
    _copy_template_snapshot,
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

    def test_template_root_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cookiecutter.json").write_text("{}\n", encoding="utf-8")
            (root / "{{cookiecutter.project_name}}").mkdir()
            (root / "hooks").mkdir()
            self.assertTrue(is_cookiecutter_template_root(root))

    def test_clean_inplace_keeps_git_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".gitignore").write_text("old\n", encoding="utf-8")
            (root / "README.md").write_text("bye\n", encoding="utf-8")
            (root / "hooks").mkdir()
            (root / "hooks" / "x.py").write_text("x\n", encoding="utf-8")

            removed = clean_inplace_target(root)
            self.assertEqual(set(removed), {"README.md", "hooks"})
            self.assertTrue((root / ".git").is_dir())
            self.assertEqual((root / ".gitignore").read_text(encoding="utf-8"), "old\n")
            self.assertEqual(list_non_git_entries(root), [])
            assert_inplace_target_ok(root)

    def test_copy_template_snapshot_survives_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cookiecutter.json").write_text('{"a":1}\n', encoding="utf-8")
            proj = root / "{{cookiecutter.project_name}}"
            proj.mkdir()
            (proj / "README.md").write_text("tpl\n", encoding="utf-8")
            (root / "hooks").mkdir()
            (root / "hooks" / "x.py").write_text("x\n", encoding="utf-8")

            snapshot = _copy_template_snapshot(root)
            try:
                self.assertTrue((snapshot / "cookiecutter.json").is_file())
                self.assertTrue(
                    (snapshot / "{{cookiecutter.project_name}}" / "README.md").is_file()
                )
                clean_inplace_target(root)
                self.assertFalse((root / "cookiecutter.json").exists())
                # Snapshot still intact after cleaning the original.
                self.assertEqual(
                    (snapshot / "cookiecutter.json").read_text(encoding="utf-8"),
                    '{"a":1}\n',
                )
            finally:
                import shutil

                shutil.rmtree(snapshot, ignore_errors=True)

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

    def test_flatten_when_package_name_equals_project_name(self) -> None:
        """Regression: project_name == project_slug used to collide on move."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".gitignore").write_text("old\n", encoding="utf-8")

            generated = root / "saryzd"
            generated.mkdir()
            pkg = generated / "saryzd"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (generated / "manage.py").write_text("print(1)\n", encoding="utf-8")
            (generated / ".gitignore").write_text("new\n", encoding="utf-8")

            flatten_generated_project(root, "saryzd")

            self.assertTrue((root / ".git").is_dir())
            # Package landed at root/saryzd (same path name as the old cookiecutter folder).
            self.assertTrue((root / "saryzd" / "__init__.py").is_file())
            self.assertTrue((root / "manage.py").is_file())
            self.assertFalse((root / "saryzd" / "saryzd").exists())
            self.assertEqual((root / ".gitignore").read_text(encoding="utf-8"), "new\n")
            # No leftover staging dir.
            self.assertFalse(any(root.glob(".dsg_inplace_*")))


if __name__ == "__main__":
    unittest.main()
