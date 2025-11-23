"""Shared test fixtures and utilities for bunenv tests."""

import io
import json
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock

import pytest


# ===== GitHub API Mock Fixtures =====


@pytest.fixture
def mock_github_releases() -> List[Dict[str, Any]]:
    """Realistic GitHub releases API response for Bun."""
    return [
        {
            "tag_name": "bun-v1.0.0",
            "draft": False,
            "prerelease": False,
            "assets": [
                {"name": "bun-darwin-aarch64.zip"},
                {"name": "bun-darwin-x64.zip"},
                {"name": "bun-linux-x64.zip"},
                {"name": "bun-linux-x64-musl.zip"},
                {"name": "bun-windows-x64.zip"},
            ],
        },
        {
            "tag_name": "bun-v0.9.0",
            "draft": False,
            "prerelease": False,
            "assets": [
                {"name": "bun-darwin-aarch64.zip"},
                {"name": "bun-linux-x64.zip"},
            ],
        },
        {
            "tag_name": "bun-v0.8.5",
            "draft": False,
            "prerelease": False,
            "assets": [
                {"name": "bun-linux-x64.zip"},
            ],
        },
        {
            "tag_name": "bun-v0.8.0-canary.1",
            "draft": False,
            "prerelease": True,
            "assets": [],
        },
    ]


@pytest.fixture(autouse=True)
def mock_urlopen(request: Any, monkeypatch: pytest.MonkeyPatch, mock_github_releases: List[Dict[str, Any]]) -> Callable:
    """Mock urllib.request.urlopen for GitHub API and file downloads.

    Auto-applied to all tests to prevent real network calls.
    Tests can opt out by using the 'no_mock_urlopen' marker.
    """
    # Skip mocking for tests that explicitly test urlopen behavior
    if "no_mock_urlopen" in request.keywords:
        return lambda *args, **kwargs: None

    def fake_urlopen(request_obj: Any, context: Any = None) -> io.BytesIO:
        """Fake urlopen that returns mock data based on URL."""
        if hasattr(request_obj, "get_full_url"):
            url = request_obj.get_full_url()
        else:
            url = str(request_obj)

        # GitHub API
        if "api.github.com/repos/oven-sh/bun/releases" in url:
            data = json.dumps(mock_github_releases).encode("utf-8")
            mock_response = io.BytesIO(data)
            return mock_response

        # Binary downloads
        if "github.com/oven-sh/bun/releases/download" in url:
            # Return fake binary content (minimal valid ZIP structure)
            import zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                zf.writestr("bun-linux-x64/bun", b"#!/bin/sh\necho '1.0.0'\n")
            zip_buffer.seek(0)
            return zip_buffer

        raise ValueError(f"Unexpected URL in test: {url}")

    # Patch both the urllib2 module (which is urllib.request in Python 3)
    import bunenv
    try:
        import urllib.request as urllib2
    except ImportError:
        import urllib2  # type: ignore

    monkeypatch.setattr(urllib2, "urlopen", fake_urlopen)

    return fake_urlopen


# ===== Platform Mock Fixtures =====


@pytest.fixture
def mock_platform(monkeypatch: pytest.MonkeyPatch) -> Callable:
    """Factory fixture for mocking platform.system() and platform.machine()."""

    def _mock(system: str = "Linux", machine: str = "x86_64") -> None:
        """Mock platform detection."""
        import platform

        monkeypatch.setattr(platform, "system", lambda: system)
        monkeypatch.setattr(platform, "machine", lambda: machine)

    return _mock


@pytest.fixture
def mock_linux_x64(mock_platform: Callable, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Linux x86_64 platform."""
    mock_platform(system="Linux", machine="x86_64")
    import bunenv
    monkeypatch.setattr(bunenv, "is_WIN", False)
    monkeypatch.setattr(bunenv, "is_CYGWIN", False)


@pytest.fixture
def mock_darwin_arm(mock_platform: Callable, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock macOS ARM64 platform."""
    mock_platform(system="Darwin", machine="ARM64")
    import bunenv
    monkeypatch.setattr(bunenv, "is_WIN", False)
    monkeypatch.setattr(bunenv, "is_CYGWIN", False)


@pytest.fixture
def mock_windows(mock_platform: Callable, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Windows platform."""
    mock_platform(system="Windows", machine="AMD64")
    import bunenv
    monkeypatch.setattr(bunenv, "is_WIN", True)
    monkeypatch.setattr(bunenv, "is_CYGWIN", False)


# ===== File System Mock Fixtures =====


@pytest.fixture
def mock_bun_binary(tmp_path: Any) -> Callable:
    """Factory to create fake Bun binary for testing."""

    def _create_binary(version: str = "1.0.0", platform: str = "linux", arch: str = "x64") -> str:
        """Create a fake Bun binary structure in tmp_path."""
        bun_dir = tmp_path / f"bun-{platform}-{arch}"
        bun_dir.mkdir(exist_ok=True)

        binary_name = "bun.exe" if platform == "windows" else "bun"
        binary_path = bun_dir / binary_name
        binary_path.write_bytes(b"#!/bin/sh\necho '1.0.0'\n")

        return str(bun_dir.parent)

    return _create_binary


@pytest.fixture
def mock_zipfile_extract(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """Mock zipfile extraction to create fake Bun structure."""

    def fake_extractall(self: Any, path: str) -> None:
        """Create fake extracted structure."""
        import os

        bun_dir = os.path.join(path, "bun-linux-x64")
        os.makedirs(bun_dir, exist_ok=True)
        bun_binary = os.path.join(bun_dir, "bun")
        with open(bun_binary, "wb") as f:
            f.write(b"#!/bin/sh\necho '1.0.0'\n")

    import zipfile

    monkeypatch.setattr(zipfile.ZipFile, "extractall", fake_extractall)


# ===== Subprocess Mock Fixtures =====


@pytest.fixture
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> Callable:
    """Mock subprocess.Popen for command execution."""

    def _mock_popen(
        stdout: str = "",
        stderr: str = "",
        returncode: int = 0,
    ) -> Callable:
        """Create a mock Popen that returns specified output."""

        class MockPopen:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.returncode = returncode
                self.stdout = io.BytesIO(stdout.encode("utf-8")) if stdout else None
                self.stderr = io.BytesIO(stderr.encode("utf-8")) if stderr else None
                self.args = args
                self.kwargs = kwargs

            def communicate(self) -> tuple[bytes, bytes]:
                stdout_data = self.stdout.read() if self.stdout else b""
                stderr_data = self.stderr.read() if self.stderr else b""
                return stdout_data, stderr_data

            def wait(self) -> int:
                return self.returncode

            def readline(self) -> bytes:
                if self.stdout:
                    return self.stdout.readline()
                return b""

        import subprocess

        monkeypatch.setattr(subprocess, "Popen", MockPopen)
        return MockPopen

    return _mock_popen


# ===== Config File Mock Fixtures =====


@pytest.fixture
def mock_config_file(tmp_path: Any) -> Callable:
    """Factory to create mock config files."""

    def _create(content: str, filename: str = ".bunenvrc") -> str:
        """Create a config file with specified content."""
        config_path = tmp_path / filename
        config_path.write_text(content)
        return str(config_path)

    return _create


@pytest.fixture
def sample_bunenvrc(tmp_path: Any) -> str:
    """Create a sample .bunenvrc config file."""
    config = tmp_path / ".bunenvrc"
    config.write_text(
        """[bunenv]
bun = 1.0.0
variant = musl
github_token = fake_token_12345
"""
    )
    return str(config)


@pytest.fixture
def sample_bun_version_file(tmp_path: Any) -> str:
    """Create a sample .bun-version file."""
    version_file = tmp_path / ".bun-version"
    version_file.write_text("1.3.0\n")
    return str(version_file)


# ===== SSL Context Mock =====


@pytest.fixture
def mock_ssl_context(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock SSL context creation for ignore_ssl_certs tests."""
    import ssl

    mock_context = MagicMock()
    monkeypatch.setattr(ssl, "SSLContext", lambda protocol: mock_context)


# ===== Environment Mocks =====


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables for isolated tests."""
    import os

    # Remove bunenv-related env vars
    for key in list(os.environ.keys()):
        if "BUN" in key:
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def mock_virtualenv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Python virtualenv detection."""
    import sys

    monkeypatch.setattr(sys, "real_prefix", "/usr", raising=False)


# ===== Reset Global State =====


@pytest.fixture(autouse=True)
def reset_config() -> None:
    """Reset Config class to defaults before each test."""
    import bunenv

    # Reset to defaults
    for attr, val in bunenv.Config._default.items():
        setattr(bunenv.Config, attr, val)

    # Reset ignore_ssl_certs
    bunenv.ignore_ssl_certs = False


@pytest.fixture(autouse=True)
def reset_logger() -> None:
    """Reset logger state before each test."""
    import bunenv

    # Create fresh logger
    bunenv.logger = bunenv.create_logger()


# ===== Helper Functions =====


@pytest.fixture
def assert_file_exists() -> Callable:
    """Helper to assert file exists and optionally check content."""

    def _assert(path: str, contains: str | None = None) -> None:
        import os

        assert os.path.exists(path), f"File not found: {path}"
        if contains:
            with open(path) as f:
                content = f.read()
                assert contains in content, f"Expected content not found in {path}"

    return _assert


@pytest.fixture
def assert_executable() -> Callable:
    """Helper to assert file is executable."""

    def _assert(path: str) -> None:
        import os
        import stat

        st = os.stat(path)
        assert st.st_mode & stat.S_IXUSR, f"File not executable: {path}"

    return _assert
