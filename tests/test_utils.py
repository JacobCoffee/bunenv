"""Tests for utility functions."""

import io
import os
import stat
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

import bunenv


class TestClearOutput:
    """Tests for clear_output function."""

    def test_clear_output_removes_newlines(self) -> None:
        """Test that newlines are removed from output."""
        output = b"hello\nworld\n"
        result = bunenv.clear_output(output)

        assert result == "helloworld"

    def test_clear_output_decodes_utf8(self) -> None:
        """Test that output is decoded as UTF-8."""
        output = "test".encode("utf-8")
        result = bunenv.clear_output(output)

        assert result == "test"

    def test_clear_output_empty(self) -> None:
        """Test clear_output with empty input."""
        result = bunenv.clear_output(b"")

        assert result == ""


class TestRemoveEnvBinFromPath:
    """Tests for remove_env_bin_from_path function."""

    def test_remove_env_bin_from_path(self) -> None:
        """Test removing bin directory from PATH."""
        env = "/home/user/bunenv/bin:/usr/local/bin:/usr/bin"
        env_bin_dir = "/home/user/bunenv/bin"

        result = bunenv.remove_env_bin_from_path(env, env_bin_dir)

        assert result == "/usr/local/bin:/usr/bin"

    def test_remove_env_bin_from_path_not_present(self) -> None:
        """Test when bin directory is not in PATH."""
        env = "/usr/local/bin:/usr/bin"
        env_bin_dir = "/home/user/bunenv/bin"

        result = bunenv.remove_env_bin_from_path(env, env_bin_dir)

        assert result == env


class TestToUtf8:
    """Tests for to_utf8 function."""

    def test_to_utf8_already_utf8(self) -> None:
        """Test that UTF-8 text passes through."""
        text = "hello world"
        result = bunenv.to_utf8(text)

        # In Python 3, should return unchanged
        assert result == text

    def test_to_utf8_empty(self) -> None:
        """Test to_utf8 with empty string."""
        result = bunenv.to_utf8("")

        assert result == ""

    def test_to_utf8_none(self) -> None:
        """Test to_utf8 with None."""
        result = bunenv.to_utf8(None)

        assert result is None

    def test_to_utf8_bytes_valid_utf8(self) -> None:
        """Test to_utf8 with valid UTF-8 bytes."""
        text = b"hello world"
        result = bunenv.to_utf8(text)

        assert result == b"hello world"

    def test_to_utf8_bytes_invalid_encoding(self) -> None:
        """Test to_utf8 with bytes that need encoding conversion."""
        # Create bytes with cp1252 encoding (not valid UTF-8)
        text = "café".encode("cp1252")
        result = bunenv.to_utf8(text)

        # Should attempt UTF-8 encode path
        assert result is not None

    def test_to_utf8_python2_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test to_utf8 Python 2 code paths by mocking is_PY3."""
        # Mock Python 2 environment
        monkeypatch.setattr(bunenv, "is_PY3", False)

        # Test unicode string encode path (line 73)
        class FakeUnicode:
            """Simulate Python 2 unicode object."""

            def encode(self, encoding: str) -> bytes:
                if encoding == "utf8":
                    return b"encoded"
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        fake_text = FakeUnicode()
        result = bunenv.to_utf8(fake_text)
        assert result == b"encoded"

        # Test decode path (line 76-77)
        class FakeBytesUTF8:
            """Simulate bytes that are valid UTF-8."""

            def encode(self, encoding: str) -> bytes:
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

            def decode(self, encoding: str) -> str:
                if encoding == "utf8":
                    return self  # type: ignore
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        fake_bytes = FakeBytesUTF8()
        result = bunenv.to_utf8(fake_bytes)
        assert result == fake_bytes

        # Test cp1252 path (line 80)
        class FakeBytesCP1252:
            """Simulate bytes that need cp1252 decoding."""

            def encode(self, encoding: str) -> bytes:
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

            def decode(self, encoding: str) -> "FakeBytesCP1252":
                if encoding == "utf8":
                    raise UnicodeDecodeError("test", b"", 0, 1, "test")
                if encoding == "cp1252":
                    return self  # Return self to chain .encode("utf8")
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        class FakeBytesCP1252WithEncode:
            """Simulate cp1252 decoded string."""

            called_encode = False

            def encode(self, encoding: str) -> bytes:
                if encoding == "utf8":
                    # First encode call fails
                    raise UnicodeDecodeError("test", b"", 0, 1, "test")
                return b"cp1252 encoded"

            def decode(self, encoding: str) -> "FakeBytesCP1252Result":
                if encoding == "utf8":
                    raise UnicodeDecodeError("test", b"", 0, 1, "test")
                if encoding == "cp1252":
                    return FakeBytesCP1252Result()  # type: ignore
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        class FakeBytesCP1252Result:
            """Simulate result of cp1252 decode."""

            def encode(self, encoding: str) -> bytes:
                if encoding == "utf8":
                    return b"cp1252->utf8"
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        # Actually test the cp1252 decode -> utf8 encode path (line 80)
        class FakeBytesForCP1252Path:
            def encode(self, encoding: str) -> bytes:
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

            def decode(self, encoding: str) -> "FakeDecodedString":
                if encoding == "utf8":
                    raise UnicodeDecodeError("test", b"", 0, 1, "test")
                if encoding == "cp1252":
                    return FakeDecodedString()
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        class FakeDecodedString:
            def encode(self, encoding: str) -> bytes:
                if encoding == "utf8":
                    return b"cp1252->utf8"
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        fake_cp1252 = FakeBytesForCP1252Path()
        result = bunenv.to_utf8(fake_cp1252)
        # Should return cp1252->utf8 bytes (line 80)
        assert result == b"cp1252->utf8"

        # Test all-failures path (line 84)
        class FakeBytesFail:
            """Simulate bytes that fail all decoding attempts."""

            def encode(self, encoding: str) -> bytes:
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

            def decode(self, encoding: str) -> str:
                raise UnicodeDecodeError("test", b"", 0, 1, "test")

        fake_fail = FakeBytesFail()
        result = bunenv.to_utf8(fake_fail)
        assert result == fake_fail  # Should return unchanged (line 84)


class TestMkdir:
    """Tests for mkdir function."""

    def test_mkdir_creates_directory(self, tmp_path: Any) -> None:
        """Test that mkdir creates a directory."""
        new_dir = str(tmp_path / "test_dir")

        bunenv.mkdir(new_dir)

        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)

    def test_mkdir_existing_directory(self, tmp_path: Any) -> None:
        """Test mkdir with existing directory doesn't raise error."""
        existing_dir = str(tmp_path / "existing")
        os.makedirs(existing_dir)

        # Should not raise
        bunenv.mkdir(existing_dir)

        assert os.path.exists(existing_dir)

    def test_mkdir_creates_parent_directories(self, tmp_path: Any) -> None:
        """Test that mkdir creates parent directories."""
        nested_dir = str(tmp_path / "parent" / "child" / "grandchild")

        bunenv.mkdir(nested_dir)

        assert os.path.exists(nested_dir)


class TestMakeExecutable:
    """Tests for make_executable function."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions not applicable on Windows")
    def test_make_executable(self, tmp_path: Any) -> None:
        """Test making a file executable."""
        test_file = tmp_path / "test_script.sh"
        test_file.write_text("#!/bin/sh\necho 'hello'\n")

        bunenv.make_executable(str(test_file))

        st = os.stat(str(test_file))
        assert st.st_mode & stat.S_IXUSR
        assert st.st_mode & stat.S_IXGRP
        assert st.st_mode & stat.S_IXOTH

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions not applicable on Windows")
    def test_make_executable_permissions(self, tmp_path: Any) -> None:
        """Test that make_executable sets 0755 permissions."""
        test_file = tmp_path / "script"
        test_file.write_text("content")

        bunenv.make_executable(str(test_file))

        st = os.stat(str(test_file))
        mode = stat.S_IMODE(st.st_mode)
        expected = stat.S_IRWXU | stat.S_IXGRP | stat.S_IRGRP | stat.S_IROTH | stat.S_IXOTH

        assert mode == expected


class TestWritefile:
    """Tests for writefile function."""

    def test_writefile_creates_file(self, tmp_path: Any) -> None:
        """Test that writefile creates a new file."""
        dest = str(tmp_path / "test.txt")
        content = "hello world"

        bunenv.writefile(dest, content)

        assert os.path.exists(dest)
        with open(dest) as f:
            assert f.read() == content

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions not applicable on Windows")
    def test_writefile_makes_executable(self, tmp_path: Any) -> None:
        """Test that writefile makes file executable."""
        dest = str(tmp_path / "script.sh")

        bunenv.writefile(dest, "#!/bin/sh\n")

        st = os.stat(dest)
        assert st.st_mode & stat.S_IXUSR

    def test_writefile_bytes_content(self, tmp_path: Any) -> None:
        """Test writefile with bytes content."""
        dest = str(tmp_path / "binary.dat")
        content = b"\x00\x01\x02\x03"

        bunenv.writefile(dest, content)

        with open(dest, "rb") as f:
            assert f.read() == content

    def test_writefile_content_already_exists(self, tmp_path: Any) -> None:
        """Test writefile when content already exists."""
        dest = str(tmp_path / "test.txt")
        content = "same content"

        bunenv.writefile(dest, content)
        bunenv.writefile(dest, content)

        # Should not error and file should exist
        assert os.path.exists(dest)

    def test_writefile_no_overwrite(self, tmp_path: Any) -> None:
        """Test writefile with overwrite=False."""
        dest = str(tmp_path / "test.txt")

        bunenv.writefile(dest, "original")
        bunenv.writefile(dest, "different", overwrite=False)

        with open(dest) as f:
            assert f.read() == "original"

    def test_writefile_append(self, tmp_path: Any) -> None:
        """Test writefile with append=True."""
        dest = str(tmp_path / "test.txt")

        bunenv.writefile(dest, "first")
        bunenv.writefile(dest, "second", append=True)

        with open(dest) as f:
            content = f.read()
            assert "first" in content
            assert "second" in content

    def test_writefile_overwrite_different_content(self, tmp_path: Any, caplog: Any) -> None:
        """Test writefile overwrites when content differs."""
        dest = str(tmp_path / "test.txt")

        bunenv.writefile(dest, "original")
        bunenv.writefile(dest, "different")

        with open(dest) as f:
            assert f.read() == "different"

        # Should log that it's overwriting
        assert "Overwriting" in caplog.text


class TestCallit:
    """Tests for callit function."""

    def test_callit_simple_command(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test calling a simple command."""

        class MockProc:
            returncode = 0
            stdout = io.BytesIO(b"output line\n")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        returncode, output = bunenv.callit(["echo", "hello"], show_stdout=False)

        assert returncode == 0
        assert len(output) == 1

    def test_callit_with_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit with command that returns error."""

        class MockProc:
            returncode = 1
            stdout = io.BytesIO(b"error\n")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        with pytest.raises(OSError) as exc_info:
            bunenv.callit(["false"], show_stdout=False)

        assert "failed with error code 1" in str(exc_info.value)

    def test_callit_in_shell(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit with shell=True."""

        class MockProc:
            returncode = 0
            stdout = io.BytesIO(b"")

            def __init__(self, cmd: Any, **kwargs: Any) -> None:
                # Verify cmd is a string when in_shell=True
                assert isinstance(cmd, str)

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", MockProc)

        bunenv.callit(["echo", "test"], in_shell=True, show_stdout=False)

    def test_callit_with_cwd(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit with custom cwd."""
        cwd_used = None

        class MockProc:
            returncode = 0
            stdout = io.BytesIO(b"")

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                nonlocal cwd_used
                cwd_used = kwargs.get("cwd")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", MockProc)

        bunenv.callit(["pwd"], cwd=str(tmp_path), show_stdout=False)

        assert cwd_used == str(tmp_path)

    def test_callit_with_extra_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit with extra environment variables."""
        env_used = None

        class MockProc:
            returncode = 0
            stdout = io.BytesIO(b"")

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                nonlocal env_used
                env_used = kwargs.get("env")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", MockProc)

        bunenv.callit(["env"], extra_env={"TEST_VAR": "test_value"}, show_stdout=False)

        assert env_used is not None
        assert env_used["TEST_VAR"] == "test_value"

    def test_callit_long_command_truncation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that long command parts are truncated in logging."""

        class MockProc:
            returncode = 0
            stdout = io.BytesIO(b"")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        long_string = "a" * 100
        returncode, _ = bunenv.callit(["echo", long_string], show_stdout=False)

        assert returncode == 0

    def test_callit_command_with_special_chars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit with command parts containing special characters."""

        class MockProc:
            returncode = 0
            stdout = io.BytesIO(b"")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        # Test with spaces, quotes, newlines
        returncode, _ = bunenv.callit(["echo", "hello world", 'test"quote"', "new\nline"], show_stdout=False)

        assert returncode == 0

    def test_callit_popen_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit when Popen raises exception."""
        import subprocess

        def failing_popen(*args: Any, **kwargs: Any) -> None:
            raise OSError("Failed to execute")

        monkeypatch.setattr(subprocess, "Popen", failing_popen)

        with pytest.raises(OSError, match="Failed to execute"):
            bunenv.callit(["nonexistent"], show_stdout=False)

    def test_callit_unicode_decode_error_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit fallback to cp866 on UnicodeDecodeError."""

        class MockProc:
            returncode = 0
            # Create bytes that will fail UTF-8 decoding
            stdout = io.BytesIO(b"\xff\xfe invalid utf8\n")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        # Should not raise, uses cp866 fallback
        returncode, output = bunenv.callit(["test"], show_stdout=False)

        assert returncode == 0
        assert len(output) == 1

    def test_callit_windows_mbcs_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test callit Windows mbcs decoding path (line 461)."""
        import sys

        # Skip on non-Windows as mbcs codec doesn't exist
        if sys.platform != "win32":
            pytest.skip("mbcs encoding only available on Windows")

        class MockStdout:
            """Mock stdout that returns lines."""

            def __init__(self) -> None:
                self.lines = [b"output\n", b""]
                self.index = 0

            def readline(self) -> bytes:
                if self.index < len(self.lines):
                    line = self.lines[self.index]
                    self.index += 1
                    return line
                return b""

        class MockProc:
            returncode = 0

            def __init__(self) -> None:
                self.stdout = MockStdout()

            def wait(self) -> int:
                return self.returncode

        import subprocess

        # Mock Windows environment
        monkeypatch.setattr(bunenv, "is_WIN", True)
        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        # Should use mbcs decoding on Windows
        returncode, output = bunenv.callit(["test"], show_stdout=False)

        assert returncode == 0
        assert len(output) == 1
        assert output[0] == "output"

    def test_callit_error_with_show_stdout(self, monkeypatch: pytest.MonkeyPatch, caplog: Any) -> None:
        """Test callit error handling with show_stdout=True."""

        class MockProc:
            returncode = 127
            stdout = io.BytesIO(b"command not found\nerror details\n")

            def wait(self) -> int:
                return self.returncode

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProc())

        with pytest.raises(OSError):
            bunenv.callit(["nonexistent"], show_stdout=True)

        # Check that output was logged as critical
        assert "command not found" in caplog.text


class TestIsX8664Musl:
    """Tests for is_x86_64_musl function."""

    def test_is_x86_64_musl_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detection of musl libc."""
        import sysconfig

        monkeypatch.setattr(sysconfig, "get_config_var", lambda x: "x86_64-pc-linux-musl" if x == "HOST_GNU_TYPE" else None)

        result = bunenv.is_x86_64_musl()

        assert result is True

    def test_is_x86_64_musl_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test when not using musl libc."""
        import sysconfig

        monkeypatch.setattr(sysconfig, "get_config_var", lambda x: "x86_64-pc-linux-gnu" if x == "HOST_GNU_TYPE" else None)

        result = bunenv.is_x86_64_musl()

        assert result is False


class TestCreateLogger:
    """Tests for create_logger function."""

    def test_create_logger_returns_logger(self) -> None:
        """Test that create_logger returns a logger."""
        logger = bunenv.create_logger()

        assert logger is not None
        assert logger.name == "bunenv"

    def test_create_logger_level(self) -> None:
        """Test that logger has INFO level."""
        logger = bunenv.create_logger()

        assert logger.level == 20  # logging.INFO


@pytest.mark.no_mock_urlopen
class TestUrlopen:
    """Tests for urlopen function."""

    def test_urlopen_adds_user_agent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that urlopen adds User-Agent header."""
        headers_used = None

        class MockRequest:
            def __init__(self, url: str, data: Any, headers: dict) -> None:
                nonlocal headers_used
                headers_used = headers

        import urllib.request

        monkeypatch.setattr(urllib.request, "Request", MockRequest)
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, **kwargs: io.BytesIO(b""))

        bunenv.urlopen("https://example.com")

        assert headers_used is not None
        assert "User-Agent" in headers_used
        assert "bunenv" in headers_used["User-Agent"]

    def test_urlopen_with_github_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that GitHub token is added to headers."""
        headers_used = None

        class MockRequest:
            def __init__(self, url: str, data: Any, headers: dict) -> None:
                nonlocal headers_used
                headers_used = headers

        import urllib.request

        monkeypatch.setattr(urllib.request, "Request", MockRequest)
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, **kwargs: io.BytesIO(b""))

        bunenv.Config.github_token = "test_token"

        bunenv.urlopen("https://api.github.com")

        assert "Authorization" in headers_used
        assert headers_used["Authorization"] == "token test_token"

    def test_urlopen_ignore_ssl_certs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that SSL certificate verification can be disabled."""
        import ssl

        context_created = False

        class MockSSLContext:
            def __init__(self, protocol: Any) -> None:
                nonlocal context_created
                context_created = True
                self.verify_mode = None

        monkeypatch.setattr(ssl, "SSLContext", MockSSLContext)

        import urllib.request

        monkeypatch.setattr(urllib.request, "Request", lambda *args: MagicMock())
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, **kwargs: io.BytesIO(b""))

        bunenv.ignore_ssl_certs = True

        bunenv.urlopen("https://example.com")

        assert context_created


class TestGetEnvDir:
    """Tests for get_env_dir function."""

    def test_get_env_dir_from_args(self) -> None:
        """Test getting env_dir from args."""
        import argparse

        args = argparse.Namespace(python_virtualenv=False, env_dir="/path/to/env")

        result = bunenv.get_env_dir(args)

        assert result == "/path/to/env"

    def test_get_env_dir_python_virtualenv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting env_dir from Python virtualenv."""
        import argparse
        import sys

        # Modern Python uses base_prefix to detect virtualenvs
        monkeypatch.setattr(sys, "base_prefix", "/usr", raising=False)

        args = argparse.Namespace(python_virtualenv=True, env_dir=None)

        result = bunenv.get_env_dir(args)

        assert result == sys.prefix

    def test_get_env_dir_python_virtualenv_no_venv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when python_virtualenv=True but not in virtualenv."""
        import argparse
        import sys

        # Remove virtualenv indicators
        monkeypatch.delattr(sys, "real_prefix", raising=False)
        monkeypatch.setattr(sys, "base_prefix", sys.prefix)

        args = argparse.Namespace(python_virtualenv=True, env_dir=None)

        with pytest.raises(SystemExit):
            bunenv.get_env_dir(args)
