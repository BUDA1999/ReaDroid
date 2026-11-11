from __future__ import annotations
import re
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from readroid import app

ANSI = re.compile(r"\x1b\[[0-9;]*m")

class MenuRenderingTests(unittest.TestCase):
    def render(self, columns):
        output=[]
        with patch.object(app, "width", return_value=columns), \
             patch.object(app, "ai_available", return_value=False), \
             patch("builtins.print", side_effect=lambda *a, **k: output.append(" ".join(map(str, a)))):
            app.print_menu()
        return "\n".join(ANSI.sub("", line) for line in output)

    def test_menu_contains_title_status_options_and_exit(self):
        result=self.render(44)
        self.assertIn("RE A DROID", result)
        self.assertIn("SYSTEM", result)
        for key in ("[ 1]", "[ 4]", "[ 6]", "[11]", "[14]", "[ 0]"):
            self.assertIn(key, result)

    def test_narrow_terminal_does_not_omit_actions(self):
        result=self.render(32)
        self.assertIn("Reconstruir", result)
        self.assertIn("Idioma", result)
        self.assertIn("Sair", result)

    def test_wide_terminal_keeps_rows_within_terminal_width(self):
        result=self.render(78)
        for line in result.splitlines():
            if line.strip():
                self.assertLessEqual(len(line), 78)

