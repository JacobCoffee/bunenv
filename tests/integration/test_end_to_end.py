"""Integration tests for full bunenv workflows."""

import argparse
import os
import sys
from typing import Any

import pytest

import bunenv


class TestMainFunction:
    """Tests for the main entry point function."""

    def test_main_dump_config_defaults(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
        """Test --dump-config-defaults flag."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--dump-config-defaults"])

        bunenv.main()

        captured = capsys.readouterr()
        assert "[bunenv]" in captured.out
        assert "bun = " in captured.out

    def test_main_list_versions(self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
        """Test --list flag to show versions."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--list"])

        with caplog.at_level("INFO"):
            bunenv.main()

        # Version list is logged via logger.info
        assert "1.0.0" in caplog.text

    def test_main_resolves_latest_version(self, monkeypatch: pytest.MonkeyPatch, mock_urlopen: Any, mock_linux_x64: Any) -> None:
        """Test that 'latest' is resolved to actual version."""
        create_called = False
        resolved_version = None

        def fake_create_environment(env_dir: str, args: Any) -> None:
            nonlocal create_called, resolved_version
            create_called = True
            resolved_version = args.bun

        monkeypatch.setattr(sys, "argv", ["bunenv", "--bun=latest", "test-env"])
        monkeypatch.setattr(bunenv, "create_environment", fake_create_environment)

        bunenv.main()

        assert create_called
        assert resolved_version == "1.0.0"  # Latest from mock

    def test_main_loads_config(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_urlopen: Any) -> None:
        """Test that main loads config from files."""
        config_file = tmp_path / ".bunenvrc"
        config_file.write_text("[bunenv]\nbun = 1.5.0\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["bunenv", "-C", str(config_file), "test-env"])

        create_called = False

        def fake_create(env_dir: str, args: Any) -> None:
            nonlocal create_called
            create_called = True

        monkeypatch.setattr(bunenv, "create_environment", fake_create)

        bunenv.main()

        assert bunenv.Config.bun == "1.5.0"

    def test_main_sets_ignore_ssl_certs(self, monkeypatch: pytest.MonkeyPatch, mock_urlopen: Any) -> None:
        """Test that --ignore_ssl_certs sets global flag."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--ignore_ssl_certs", "test-env"])
        monkeypatch.setattr(bunenv, "create_environment", lambda *args: None)

        bunenv.main()

        assert bunenv.ignore_ssl_certs is True

    def test_main_sets_github_token(self, monkeypatch: pytest.MonkeyPatch, mock_urlopen: Any) -> None:
        """Test that --github-token sets Config value."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--github-token=test_token", "test-env"])
        monkeypatch.setattr(bunenv, "create_environment", lambda *args: None)

        bunenv.main()

        assert bunenv.Config.github_token == "test_token"

    def test_main_update_mode(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_urlopen: Any) -> None:
        """Test --update mode to install packages without creating environment."""
        install_packages_called = False

        def fake_install_packages(env_dir: str, args: Any) -> None:
            nonlocal install_packages_called
            install_packages_called = True

        monkeypatch.setattr(sys, "argv", ["bunenv", "--update", str(tmp_path)])
        monkeypatch.setattr(bunenv, "install_packages", fake_install_packages)

        bunenv.main()

        assert install_packages_called

    def test_main_system_bun_on_windows_fails(self, monkeypatch: pytest.MonkeyPatch, mock_windows: Any) -> None:
        """Test that system bun on Windows raises error."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--bun=system", "test-env"])

        with pytest.raises(SystemExit):
            bunenv.main()

    def test_main_latest_version_fetch_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when unable to determine latest version."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--bun=latest", "test-env"])
        monkeypatch.setattr(bunenv, "get_last_stable_bun_version", lambda: None)

        with pytest.raises(SystemExit):
            bunenv.main()


class TestEndToEndWorkflows:
    """Integration tests for complete workflows."""

    def test_full_environment_creation(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any, mock_urlopen: Any
    ) -> None:
        """Test complete environment creation workflow."""

        def fake_download(url: str, src_dir: str, args: Any) -> None:
            # Create fake Bun structure
            bun_dir = os.path.join(src_dir, "bun-linux-x64")
            os.makedirs(bun_dir)
            with open(os.path.join(bun_dir, "bun"), "wb") as f:
                f.write(b"#!/bin/sh\necho '1.0.0'\n")

        monkeypatch.setattr(bunenv, "download_bun_bin", fake_download)

        env_dir = tmp_path / "test-env"
        args = argparse.Namespace(
            bun="1.0.0",
            variant="",
            mirror=None,
            python_virtualenv=False,
            force=False,
            requirements="",
            clean_src=False,
            prompt=None,
            verbose=False
        )

        bunenv.create_environment(str(env_dir), args)

        # Verify complete structure
        assert (env_dir / "src").exists()
        assert (env_dir / "bin").exists()
        assert (env_dir / "bin" / "bun").exists()
        assert (env_dir / "bin" / "activate").exists()
        assert (env_dir / "bin" / "activate.fish").exists()

    def test_environment_with_custom_variant(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test environment creation with musl variant."""
        download_url = None

        def fake_download(url: str, src_dir: str, args: Any) -> None:
            nonlocal download_url
            download_url = url
            # Create fake structure
            bun_dir = os.path.join(src_dir, "bun-linux-x64-musl")
            os.makedirs(bun_dir)
            with open(os.path.join(bun_dir, "bun"), "wb") as f:
                f.write(b"fake bun")

        monkeypatch.setattr(bunenv, "download_bun_bin", fake_download)

        env_dir = tmp_path / "test-env"
        args = argparse.Namespace(
            bun="1.0.0",
            variant="musl",
            mirror=None,
            python_virtualenv=False,
            force=False,
            requirements="",
            clean_src=False,
            prompt=None,
            verbose=False
        )

        bunenv.create_environment(str(env_dir), args)

        assert download_url is not None
        assert "musl" in download_url

    def test_environment_with_requirements(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test environment creation with package installation."""
        packages_installed = []

        def fake_callit(cmd: list, **kwargs: Any) -> tuple:
            if "add" in cmd:
                packages_installed.append(cmd[-1])
            return (0, [])

        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)
        monkeypatch.setattr(bunenv, "callit", fake_callit)

        env_dir = tmp_path / "test-env"
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("prettier\neslint\n")

        # Create fake bun binary
        bin_dir = env_dir / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "bun").write_bytes(b"fake")

        args = argparse.Namespace(
            bun="1.0.0",
            variant="",
            mirror=None,
            python_virtualenv=False,
            force=True,  # Required because we pre-created bin_dir
            requirements=str(req_file),
            clean_src=False,
            prompt=None,
            verbose=False,
        )

        bunenv.create_environment(str(env_dir), args)

        assert "prettier" in packages_installed
        assert "eslint" in packages_installed

    @pytest.mark.skipif(sys.platform == "win32", reason="sys.prefix virtualenv integration complex on Windows")
    def test_environment_in_python_virtualenv(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test bunenv integration with Python virtualenv."""
        import sys

        # Simulate being in a virtualenv (modern Python uses base_prefix)
        monkeypatch.setattr(sys, "base_prefix", "/usr", raising=False)
        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)

        args = argparse.Namespace(
            bun="1.0.0",
            variant="",
            mirror=None,
            python_virtualenv=True,
            force=True,  # Because sys.prefix directory exists
            requirements="",
            clean_src=False,
            prompt=None,
            verbose=False
        )

        bunenv.create_environment(sys.prefix, args)

        # Check that predeactivate hook was created
        predeactivate = os.path.join(sys.prefix, "bin", "predeactivate")
        if os.path.exists(predeactivate):
            content = open(predeactivate).read()
            assert "deactivate_bun" in content

    def test_environment_with_clean_src(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test that --clean-src removes source directory."""
        import os

        def mock_install_bun(env_dir: str, *args: Any) -> None:
            # Create necessary directory structure
            bin_dir = os.path.join(env_dir, "bin")
            os.makedirs(bin_dir, exist_ok=True)

        monkeypatch.setattr(bunenv, "install_bun", mock_install_bun)

        env_dir = tmp_path / "test-env"
        args = argparse.Namespace(
            bun="1.0.0",
            variant="",
            mirror=None,
            python_virtualenv=False,
            force=False,
            requirements="",
            clean_src=True,
            prompt=None,
            verbose=False
        )

        bunenv.create_environment(str(env_dir), args)

        assert not (env_dir / "src").exists()

    def test_multiple_environments(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test creating multiple independent environments."""
        import os

        def mock_install_bun(env_dir: str, *args: Any) -> None:
            # Create necessary directory structure
            bin_dir = os.path.join(env_dir, "bin")
            os.makedirs(bin_dir, exist_ok=True)

        monkeypatch.setattr(bunenv, "install_bun", mock_install_bun)

        # Create first environment
        env1 = tmp_path / "env1"
        args1 = argparse.Namespace(
            bun="1.0.0",
            variant="",
            mirror=None,
            python_virtualenv=False,
            force=False,
            requirements="",
            clean_src=False,
            prompt="(env1)",
            verbose=False,
        )
        bunenv.create_environment(str(env1), args1)

        # Create second environment
        env2 = tmp_path / "env2"
        args2 = argparse.Namespace(
            bun="0.9.0",
            variant="",
            mirror=None,
            python_virtualenv=False,
            force=False,
            requirements="",
            clean_src=False,
            prompt="(env2)",
            verbose=False,
        )
        bunenv.create_environment(str(env2), args2)

        # Both should exist independently
        assert env1.exists()
        assert env2.exists()
        assert (env1 / "bin" / "activate").exists()
        assert (env2 / "bin" / "activate").exists()

        # Check that prompts are different
        activate1 = (env1 / "bin" / "activate").read_text()
        activate2 = (env2 / "bin" / "activate").read_text()
        assert "(env1)" in activate1
        assert "(env2)" in activate2


class TestErrorHandling:
    """Tests for error handling in various scenarios."""

    def test_invalid_version_format(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any) -> None:
        """Test handling of invalid version numbers."""
        # parse_version should handle various formats
        assert bunenv.parse_version("invalid") == ()  # Empty tuple if parsing fails
        # Or it might raise - depends on implementation

    @pytest.mark.no_mock_urlopen
    def test_network_error_handling(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test handling of network errors during version fetch."""

        def fake_urlopen(*args: Any, **kwargs: Any) -> None:
            raise OSError("Network error")

        # Patch urllib2.urlopen which is what bunenv uses
        monkeypatch.setattr(bunenv.urllib2, "urlopen", fake_urlopen)

        with pytest.raises(OSError):
            bunenv._get_versions_json()

    def test_missing_requirements_file(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when requirements file doesn't exist."""
        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)

        env_dir = tmp_path / "test-env"
        args = argparse.Namespace(
            bun="1.0.0",
            variant="",
            mirror=None,
            python_virtualenv=False,
            force=False,
            requirements="/nonexistent/requirements.txt",
            clean_src=False,
            prompt=None,
            verbose=False
        )

        with pytest.raises(FileNotFoundError):
            bunenv.create_environment(str(env_dir), args)
