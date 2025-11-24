"""Tests for argument parsing functions."""

import sys
from typing import Any, cast

import pytest

import bunenv


class TestArgumentParser:
    """Tests for make_parser and parse_args functions."""

    def test_make_parser_returns_parser(self) -> None:
        """Test that make_parser returns an ArgumentParser."""
        parser = bunenv.make_parser()
        assert parser is not None
        assert hasattr(parser, "parse_args")

    def test_parser_version(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test --version argument."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--version"])

        with pytest.raises(SystemExit) as exc_info:
            bunenv.make_parser().parse_args()

        assert cast(SystemExit, exc_info.value).code == 0

    def test_parser_bun_argument(self) -> None:
        """Test --bun argument parsing."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--bun=1.5.0", "test-env"])

        assert args.bun == "1.5.0"

    def test_parser_bun_short_form(self) -> None:
        """Test -b short form for bun version."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["-b", "1.0.0", "test-env"])

        assert args.bun == "1.0.0"

    def test_parser_variant_argument(self) -> None:
        """Test --variant argument."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--variant=musl", "test-env"])

        assert args.variant == "musl"

    def test_parser_variant_choices(self) -> None:
        """Test that variant only accepts valid choices."""
        parser = bunenv.make_parser()

        # Valid variants
        for variant in ["", "baseline", "profile", "musl"]:
            args = parser.parse_args([f"--variant={variant}", "test-env"])
            assert args.variant == variant

        # Invalid variant
        with pytest.raises(SystemExit):
            parser.parse_args(["--variant=invalid", "test-env"])

    def test_parser_github_token(self) -> None:
        """Test --github-token argument."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--github-token=ghp_test", "test-env"])

        assert args.github_token == "ghp_test"

    def test_parser_mirror(self) -> None:
        """Test --mirror argument."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--mirror=https://example.com", "test-env"])

        assert args.mirror == "https://example.com"

    def test_parser_verbose_flag(self) -> None:
        """Test -v/--verbose flag."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-v", "test-env"])
        assert args.verbose is True

        args = parser.parse_args(["--verbose", "test-env"])
        assert args.verbose is True

    def test_parser_quiet_flag(self) -> None:
        """Test -q/--quiet flag."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-q", "test-env"])
        assert args.quiet is True

        args = parser.parse_args(["--quiet", "test-env"])
        assert args.quiet is True

    def test_parser_config_file(self) -> None:
        """Test -C/--config-file argument."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-C", "/path/to/config", "test-env"])
        assert args.config_file == "/path/to/config"

        args = parser.parse_args(["--config-file=/other/config", "test-env"])
        assert args.config_file == "/other/config"

    def test_parser_requirements(self) -> None:
        """Test -r/--requirements argument."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-r", "requirements.txt", "test-env"])
        assert args.requirements == "requirements.txt"

        args = parser.parse_args(["--requirements=reqs.txt", "test-env"])
        assert args.requirements == "reqs.txt"

    def test_parser_prompt(self) -> None:
        """Test --prompt argument."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--prompt=(my-env)", "test-env"])

        assert args.prompt == "(my-env)"

    def test_parser_list_flag(self) -> None:
        """Test -l/--list flag."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-l"])
        assert args.list is True

        args = parser.parse_args(["--list"])
        assert args.list is True

    def test_parser_update_flag(self) -> None:
        """Test --update flag."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--update", "test-env"])

        assert args.update is True

    def test_parser_python_virtualenv_flag(self) -> None:
        """Test -p/--python-virtualenv flag."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-p"])
        assert args.python_virtualenv is True

        args = parser.parse_args(["--python-virtualenv"])
        assert args.python_virtualenv is True

    def test_parser_clean_src_flag(self) -> None:
        """Test -c/--clean-src flag."""
        parser = bunenv.make_parser()

        args = parser.parse_args(["-c", "test-env"])
        assert args.clean_src is True

        args = parser.parse_args(["--clean-src", "test-env"])
        assert args.clean_src is True

    def test_parser_force_flag(self) -> None:
        """Test --force flag."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--force", "test-env"])

        assert args.force is True

    def test_parser_prebuilt_flag(self) -> None:
        """Test --prebuilt flag."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--prebuilt", "test-env"])

        assert args.prebuilt is True

    def test_parser_ignore_ssl_certs_flag(self) -> None:
        """Test --ignore_ssl_certs flag."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--ignore_ssl_certs", "test-env"])

        assert args.ignore_ssl_certs is True

    def test_parser_env_dir(self) -> None:
        """Test DEST_DIR positional argument."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["/path/to/env"])

        assert args.env_dir == "/path/to/env"

    def test_parser_env_dir_optional(self) -> None:
        """Test that DEST_DIR is optional."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["--list"])

        assert args.env_dir is None

    def test_parse_args_default_config_files(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that parse_args sets default config files."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "test-env"])

        args = bunenv.parse_args()

        assert args.config_file == ["./tox.ini", "./setup.cfg", "~/.bunenvrc"]

    def test_parse_args_empty_config_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that empty --config-file results in empty list."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--config-file=", "test-env"])

        args = bunenv.parse_args()

        assert args.config_file == []

    def test_parse_args_explicit_config_file(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that explicit config file is validated."""
        config_file = tmp_path / "custom.ini"
        config_file.write_text("[bunenv]\n")

        monkeypatch.setattr(sys, "argv", ["bunenv", f"--config-file={config_file}", "test-env"])

        args = bunenv.parse_args()

        assert args.config_file == [str(config_file)]

    def test_parse_args_missing_config_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that missing explicit config file raises error."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--config-file=/nonexistent", "test-env"])

        with pytest.raises(SystemExit):
            bunenv.parse_args()

    def test_parse_args_no_check(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test parse_args with check=False skips validation."""
        monkeypatch.setattr(sys, "argv", ["bunenv"])

        # Should not raise even without DEST_DIR
        args = bunenv.parse_args(check=False)
        assert args.env_dir is None

    def test_parse_args_requires_dest_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that parse_args requires DEST_DIR or --python-virtualenv."""
        monkeypatch.setattr(sys, "argv", ["bunenv"])

        with pytest.raises(SystemExit):
            bunenv.parse_args()

    def test_parse_args_list_no_dest_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that --list doesn't require DEST_DIR."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "--list"])

        args = bunenv.parse_args()
        assert args.list is True

    def test_parse_args_python_virtualenv_no_dest_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that --python-virtualenv doesn't require DEST_DIR."""
        monkeypatch.setattr(sys, "argv", ["bunenv", "-p"])

        args = bunenv.parse_args()
        assert args.python_virtualenv is True

    def test_parser_defaults_from_config(self) -> None:
        """Test that parser uses Config class defaults."""
        parser = bunenv.make_parser()
        args = parser.parse_args(["test-env"])

        assert args.bun == bunenv.Config.bun
        assert args.variant == bunenv.Config.variant
        assert args.github_token == bunenv.Config.github_token
        assert args.mirror == bunenv.Config.mirror
