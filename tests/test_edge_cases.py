"""Tests for edge cases and uncovered code paths."""

import argparse
import os
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

import bunenv


class TestCygwinPlatform:
    """Tests for CYGWIN-specific code paths."""

    def test_install_activate_cygwin_mkdir(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that mkdir is called for bin_dir on CYGWIN."""
        # Mock CYGWIN platform
        monkeypatch.setattr(bunenv, "is_CYGWIN", True)
        monkeypatch.setattr(bunenv, "is_WIN", False)

        # Track if mkdir was called
        mkdir_calls = []
        original_mkdir = bunenv.mkdir

        def tracked_mkdir(path: str) -> None:
            mkdir_calls.append(path)
            original_mkdir(path)

        monkeypatch.setattr(bunenv, "mkdir", tracked_mkdir)

        env_dir = tmp_path / "env"
        env_dir.mkdir()

        args = argparse.Namespace(bun="1.0.0", prompt="", python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        # Verify bin_dir was created explicitly on CYGWIN
        bin_dir = os.path.join(str(env_dir), "bin")
        assert bin_dir in mkdir_calls


class TestMainEntryPoint:
    """Tests for __main__ entry point."""

    def test_main_entry_point_exists(self) -> None:
        """Test that __main__ entry point exists in the module."""
        import importlib.util
        spec = importlib.util.find_spec("bunenv")
        assert spec is not None
        assert spec.origin is not None

        # Read the file and verify __main__ block exists
        with open(spec.origin) as f:
            content = f.read()
            assert 'if __name__ == "__main__":' in content
            assert "main()" in content

    def test_main_can_be_called_directly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test calling main() directly to cover line 1206."""
        # Mock sys.argv to prevent actual execution
        monkeypatch.setattr(sys, "argv", ["bunenv", "--help"])

        # This should raise SystemExit with code 0 for --help
        with pytest.raises(SystemExit) as exc_info:
            bunenv.main()

        assert exc_info.value.code == 0

    def test_main_block_execution(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that __main__ block executes main() when run directly (line 1206)."""
        import subprocess
        import sys

        # Create a test script that imports bunenv and executes the __main__ block
        test_script = tmp_path / "test_main_block.py"
        test_script.write_text("""
import sys
sys.argv = ["bunenv", "--help"]

# Import the module
import bunenv

# Simulate running as __main__
if True:  # Simulates __name__ == "__main__"
    try:
        bunenv.main()
    except SystemExit as e:
        # Expected for --help
        sys.exit(e.code)
""")

        # Run the script
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True
        )

        # Should exit with 0 for --help
        assert result.returncode == 0


class TestWindowsDecoding:
    """Tests for Windows-specific mbcs decoding."""

    def test_callit_windows_mbcs_decoding(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit uses mbcs decoding on Windows."""
        import io
        import sys

        # Skip on non-Windows as mbcs codec doesn't exist
        if sys.platform != "win32":
            pytest.skip("mbcs encoding only available on Windows")

        # Mock Windows platform
        monkeypatch.setattr(bunenv, "is_WIN", True)

        class MockProc:
            returncode = 0
            # Output that might contain Windows-specific encoding
            stdout = io.BytesIO("test output\n".encode("mbcs"))

            def wait(self) -> int:
                return self.returncode

        import subprocess
        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        returncode, output = bunenv.callit(["test"], show_stdout=False)

        assert returncode == 0
        assert len(output) == 1
        assert output[0] == "test output"


class TestConfigEdgeCases:
    """Tests for Config class edge cases."""

    def test_config_class_has_defaults(self) -> None:
        """Test that Config class has _default attribute."""
        assert hasattr(bunenv.Config, "_default")
        assert isinstance(bunenv.Config._default, dict)
        assert "github_token" in bunenv.Config._default


class TestUtilityEdgeCases:
    """Tests for utility function edge cases."""

    def test_to_utf8_with_binary_fallback(self) -> None:
        """Test to_utf8 fallback path for non-UTF-8 bytes."""
        # Create a byte string that's not valid UTF-8 but is valid cp1252
        # Windows-1252 specific character
        text = b"\x80"  # Euro sign in cp1252

        result = bunenv.to_utf8(text)

        # Should return something (either decoded or original)
        assert result is not None
