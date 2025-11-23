"""Tests for Config class and configuration loading."""

import os

import pytest

import bunenv


class TestConfig:
    """Tests for the Config class."""

    def test_config_defaults(self) -> None:
        """Test that Config has correct default values."""
        assert bunenv.Config.bun == "latest"
        assert bunenv.Config.variant == ""
        assert bunenv.Config.github_token is None
        assert bunenv.Config.prebuilt is True
        assert bunenv.Config.ignore_ssl_certs is False
        assert bunenv.Config.mirror is None

    def test_config_load_missing_file(self, tmp_path: any) -> None:
        """Test loading from non-existent config file."""
        fake_path = str(tmp_path / "nonexistent.ini")
        bunenv.Config._load([fake_path])

        # Should still have defaults
        assert bunenv.Config.bun == "latest"

    def test_config_load_no_bunenv_section(self, tmp_path: any) -> None:
        """Test loading config file without [bunenv] section."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("[other_section]\nkey = value\n")

        bunenv.Config._load([str(config_file)])

        # Should still have defaults
        assert bunenv.Config.bun == "latest"

    def test_config_load_bunenv_section(self, tmp_path: any) -> None:
        """Test loading config with [bunenv] section."""
        config_file = tmp_path / ".bunenvrc"
        config_file.write_text(
            """[bunenv]
bun = 1.5.0
variant = musl
github_token = ghp_test123
mirror = https://mirror.example.com
"""
        )

        bunenv.Config._load([str(config_file)])

        assert bunenv.Config.bun == "1.5.0"
        assert bunenv.Config.variant == "musl"
        assert bunenv.Config.github_token == "ghp_test123"
        assert bunenv.Config.mirror == "https://mirror.example.com"

    def test_config_load_boolean_values(self, tmp_path: any) -> None:
        """Test loading boolean config values."""
        config_file = tmp_path / ".bunenvrc"
        config_file.write_text(
            """[bunenv]
prebuilt = false
ignore_ssl_certs = true
"""
        )

        bunenv.Config._load([str(config_file)])

        assert bunenv.Config.prebuilt is False
        assert bunenv.Config.ignore_ssl_certs is True

    def test_config_load_reverse_order(self, tmp_path: any) -> None:
        """Test that config files are loaded in reverse order (later overrides earlier)."""
        config1 = tmp_path / "config1.ini"
        config1.write_text("[bunenv]\nbun = 1.0.0\n")

        config2 = tmp_path / "config2.ini"
        config2.write_text("[bunenv]\nbun = 2.0.0\n")

        # Files are processed in reverse, so config2 loads first, then config1 overrides
        bunenv.Config._load([str(config1), str(config2)])

        assert bunenv.Config.bun == "1.0.0"

    def test_config_load_with_verbose(self, tmp_path: any, capsys: pytest.CaptureFixture) -> None:
        """Test verbose output during config loading."""
        config_file = tmp_path / ".bunenvrc"
        config_file.write_text("[bunenv]\nbun = 1.0.0\n")

        bunenv.Config._load([str(config_file)], verbose=True)

        captured = capsys.readouterr()
        assert "CONFIG" in captured.out
        assert "bun = 1.0.0" in captured.out

    def test_config_load_bun_version_file(self, tmp_path: any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading version from .bun-version file."""
        monkeypatch.chdir(tmp_path)

        version_file = tmp_path / ".bun-version"
        version_file.write_text("1.3.7\n")

        bunenv.Config._load([])

        assert bunenv.Config.bun == "1.3.7"

    def test_config_load_bun_version_file_with_prefix(self, tmp_path: any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading version from .bun-version file with 'v' or 'bun-v' prefix."""
        monkeypatch.chdir(tmp_path)

        version_file = tmp_path / ".bun-version"
        version_file.write_text("bun-v1.4.0\n")

        bunenv.Config._load([])

        assert bunenv.Config.bun == "1.4.0"

    def test_config_load_bun_version_file_missing(self, tmp_path: any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that missing .bun-version file doesn't break config loading."""
        monkeypatch.chdir(tmp_path)

        bunenv.Config._load([])

        # Should still have default
        assert bunenv.Config.bun == "latest"

    def test_config_load_expanduser(self, tmp_path: any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ~ is expanded in config file paths."""
        config_file = tmp_path / ".bunenvrc"
        config_file.write_text("[bunenv]\nbun = 1.0.0\n")

        # Mock expanduser to return our tmp path
        def fake_expanduser(path: str) -> str:
            if path == "~/.bunenvrc":
                return str(config_file)
            return path

        monkeypatch.setattr(os.path, "expanduser", fake_expanduser)

        bunenv.Config._load(["~/.bunenvrc"])

        assert bunenv.Config.bun == "1.0.0"

    def test_config_dump(self, capsys: pytest.CaptureFixture) -> None:
        """Test _dump method prints config in correct format."""
        bunenv.Config._dump()

        captured = capsys.readouterr()
        assert "[bunenv]" in captured.out
        assert "bun = " in captured.out
        assert "variant = " in captured.out

    def test_config_default_dict(self) -> None:
        """Test that _default dict contains all non-private attributes."""
        assert hasattr(bunenv.Config, "_default")
        assert isinstance(bunenv.Config._default, dict)
        assert "bun" in bunenv.Config._default
        assert "variant" in bunenv.Config._default
        assert bunenv.Config._default["bun"] == "latest"

    def test_config_ignores_private_attributes(self, tmp_path: any) -> None:
        """Test that private attributes (starting with _) are not loaded from config."""
        config_file = tmp_path / ".bunenvrc"
        config_file.write_text(
            """[bunenv]
_private = should_be_ignored
bun = 1.0.0
"""
        )

        bunenv.Config._load([str(config_file)])

        assert bunenv.Config.bun == "1.0.0"
        # Private attribute should not be set
        assert not hasattr(bunenv.Config, "_private") or bunenv.Config._private != "should_be_ignored"
