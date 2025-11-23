"""Tests for version parsing and fetching functions."""

import argparse
from typing import Any, List

import pytest

import bunenv


class TestVersionParsing:
    """Tests for parse_version function."""

    def test_parse_version_simple(self) -> None:
        """Test parsing simple version strings."""
        assert bunenv.parse_version("1.0.0") == (1, 0, 0)
        assert bunenv.parse_version("2.5.3") == (2, 5, 3)
        assert bunenv.parse_version("10.20.30") == (10, 20, 30)

    def test_parse_version_with_v_prefix(self) -> None:
        """Test parsing version with 'v' prefix."""
        assert bunenv.parse_version("v1.2.3") == (1, 2, 3)
        assert bunenv.parse_version("v0.9.0") == (0, 9, 0)

    def test_parse_version_with_bun_v_prefix(self) -> None:
        """Test parsing version with 'bun-v' prefix."""
        assert bunenv.parse_version("bun-v1.0.0") == (1, 0, 0)
        assert bunenv.parse_version("bun-v2.1.3") == (2, 1, 3)

    def test_parse_version_with_build_metadata(self) -> None:
        """Test parsing version with build metadata after +."""
        assert bunenv.parse_version("1.0.0+build123") == (1, 0, 0)
        assert bunenv.parse_version("1.2.3+sha.abc123") == (1, 2, 3)

    def test_parse_version_max_three_parts(self) -> None:
        """Test that only first three parts are used."""
        assert bunenv.parse_version("1.2.3.4.5") == (1, 2, 3)

    def test_parse_version_two_parts(self) -> None:
        """Test parsing version with only two parts."""
        assert bunenv.parse_version("1.0") == (1, 0)

    def test_parse_version_one_part(self) -> None:
        """Test parsing version with only one part."""
        assert bunenv.parse_version("1") == (1,)


class TestBunVersionFromArgs:
    """Tests for bun_version_from_args function."""

    def test_bun_version_from_args_explicit_version(self) -> None:
        """Test getting version from args when explicit version is provided."""
        args = argparse.Namespace(bun="1.5.0")
        version = bunenv.bun_version_from_args(args)

        assert version == (1, 5, 0)

    def test_bun_version_from_args_system(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting version from system bun."""
        import subprocess

        def mock_popen(*args: Any, **kwargs: Any) -> Any:
            class MockProc:
                def communicate(self) -> tuple[bytes, bytes]:
                    return (b"1.3.0\n", b"")

            return MockProc()

        monkeypatch.setattr(subprocess, "Popen", mock_popen)

        args = argparse.Namespace(bun="system")
        version = bunenv.bun_version_from_args(args)

        assert version == (1, 3, 0)


class TestGetVersionsJson:
    """Tests for _get_versions_json function."""

    def test_get_versions_json_success(self, mock_urlopen: Any) -> None:
        """Test successful fetch of versions from GitHub API."""
        versions = bunenv._get_versions_json()

        assert isinstance(versions, list)
        assert len(versions) > 0
        assert "version" in versions[0]
        assert "tag_name" in versions[0]

    def test_get_versions_json_transforms_tag_names(self, mock_urlopen: Any) -> None:
        """Test that tag names are transformed correctly."""
        versions = bunenv._get_versions_json()

        # Check that bun-v prefix is removed from version
        for v in versions:
            assert not v["version"].startswith("bun-v")
            assert v["tag_name"].startswith("bun-v")

    @pytest.mark.no_mock_urlopen
    def test_get_versions_json_filters_non_bun_tags(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that non-bun tags are filtered out."""
        import io
        import json
        import urllib.request

        def fake_urlopen(req: Any, **kwargs: Any) -> io.BytesIO:
            releases = [
                {"tag_name": "bun-v1.0.0", "assets": []},
                {"tag_name": "other-v1.0.0", "assets": []},  # Should be filtered
            ]
            return io.BytesIO(json.dumps(releases).encode("utf-8"))

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        versions = bunenv._get_versions_json()

        assert len(versions) == 1
        assert versions[0]["tag_name"] == "bun-v1.0.0"

    def test_get_versions_json_includes_lts_false(self, mock_urlopen: Any) -> None:
        """Test that all versions have lts=False (Bun has no LTS)."""
        versions = bunenv._get_versions_json()

        for v in versions:
            assert v["lts"] is False

    @pytest.mark.no_mock_urlopen
    def test_get_versions_json_with_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that GitHub token is used when configured."""
        import io
        import json
        import urllib.request

        headers_used = {}

        def fake_request_init(self: Any, url: str, data: Any, headers: dict) -> None:
            nonlocal headers_used
            headers_used = headers
            self.url = url

        def fake_urlopen(req: Any, **kwargs: Any) -> io.BytesIO:
            releases = [{"tag_name": "bun-v1.0.0", "assets": []}]
            return io.BytesIO(json.dumps(releases).encode("utf-8"))

        monkeypatch.setattr(urllib.request.Request, "__init__", fake_request_init)
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        bunenv.Config.github_token = "test_token_123"

        bunenv._get_versions_json()

        assert "Authorization" in headers_used
        assert headers_used["Authorization"] == "token test_token_123"

    def test_get_versions_json_ignore_ssl(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that SSL context is created when ignore_ssl_certs is True."""
        import io
        import json
        import ssl

        ssl_context_created = False

        class MockSSLContext:
            def __init__(self, protocol: Any) -> None:
                nonlocal ssl_context_created
                ssl_context_created = True
                self.verify_mode = None

        def fake_urlopen(req: Any, context: Any = None) -> io.BytesIO:
            releases = [{"tag_name": "bun-v1.0.0", "assets": []}]
            return io.BytesIO(json.dumps(releases).encode("utf-8"))

        monkeypatch.setattr(ssl, "SSLContext", MockSSLContext)
        import urllib.request

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        bunenv.ignore_ssl_certs = True

        bunenv._get_versions_json()

        assert ssl_context_created


class TestGetBunVersions:
    """Tests for get_bun_versions function."""

    def test_get_bun_versions_returns_list(self, mock_urlopen: Any) -> None:
        """Test that get_bun_versions returns a list of version strings."""
        versions = bunenv.get_bun_versions()

        assert isinstance(versions, list)
        assert all(isinstance(v, str) for v in versions)

    def test_get_bun_versions_content(self, mock_urlopen: Any) -> None:
        """Test that version list contains expected versions."""
        versions = bunenv.get_bun_versions()

        assert "1.0.0" in versions
        assert "0.9.0" in versions
        assert "0.8.5" in versions


class TestPrintBunVersions:
    """Tests for print_bun_versions function."""

    def test_print_bun_versions(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that print_bun_versions outputs versions."""
        with caplog.at_level("INFO"):
            bunenv.print_bun_versions()

        # Output goes to logger.info
        assert "1.0.0" in caplog.text
        assert "0.9.0" in caplog.text

    def test_print_bun_versions_formatted_in_chunks(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that versions are printed in chunks of 8."""
        with caplog.at_level("INFO"):
            bunenv.print_bun_versions()

        # Check that tabs are used for formatting
        assert "\t" in caplog.text


class TestGetLastStableBunVersion:
    """Tests for get_last_stable_bun_version function."""

    def test_get_last_stable_bun_version(self, mock_urlopen: Any) -> None:
        """Test getting the last stable version."""
        version = bunenv.get_last_stable_bun_version()

        # Should return first version in list (latest)
        assert version == "1.0.0"

    def test_get_last_stable_bun_version_empty_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that None is returned when no versions are available."""

        def fake_get_versions() -> List[str]:
            return []

        monkeypatch.setattr(bunenv, "get_bun_versions", fake_get_versions)

        version = bunenv.get_last_stable_bun_version()

        assert version is None
