from __future__ import annotations
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from readroid import app


class JavaSetupTests(unittest.TestCase):
    def test_not_termux_does_not_install(self):
        with patch.dict(os.environ, {"PREFIX": "/usr"}), \
             patch.object(app.shutil, "which", return_value="/usr/bin/pkg"), \
             patch.object(app.subprocess, "run") as run:
            app.install_java_jadx()
            run.assert_not_called()

    def test_decline_does_not_install(self):
        with patch.dict(os.environ, {"PREFIX": "/data/data/com.termux/files/usr"}), \
             patch.object(app.shutil, "which", return_value="/data/data/com.termux/files/usr/bin/pkg"), \
             patch.object(app, "safe_input", return_value="n"), \
             patch.object(app.subprocess, "run") as run:
            app.install_java_jadx()
            run.assert_not_called()

    def test_installs_and_checks(self):
        def locate(name):
            return f"/data/data/com.termux/files/usr/bin/{name}"
        ok = SimpleNamespace(returncode=0, stdout="version", stderr="")
        with patch.dict(os.environ, {"PREFIX": "/data/data/com.termux/files/usr"}), \
             patch.object(app.shutil, "which", side_effect=locate), \
             patch.object(app, "safe_input", return_value="s"), \
             patch.object(app.subprocess, "run", side_effect=[ok, ok, ok]) as run, \
             patch.object(app, "print") as out:
            app.install_java_jadx()
            self.assertEqual(run.call_count, 3)
            self.assertEqual(run.call_args_list[0].args[0][1:], ["install", "openjdk-21", "jadx", "-y"])
            self.assertTrue(any("instalados e verificados" in str(call) for call in out.call_args_list))

    def test_failure_does_not_claim_success(self):
        fail = SimpleNamespace(returncode=1)
        with patch.dict(os.environ, {"PREFIX": "/data/data/com.termux/files/usr"}), \
             patch.object(app.shutil, "which", return_value="/data/data/com.termux/files/usr/bin/pkg"), \
             patch.object(app, "safe_input", return_value="s"), \
             patch.object(app.subprocess, "run", return_value=fail) as run, \
             patch.object(app, "print") as out:
            app.install_java_jadx()
            run.assert_called_once()
            self.assertFalse(any("instalados e verificados" in str(call) for call in out.call_args_list))
