"""Tests for activation script installation and environment creation."""

import argparse
import os
from typing import Any

import pytest

import bunenv


class TestInstallActivate:
    """Tests for install_activate function."""

    def test_install_activate_linux(self, tmp_path: Any, mock_linux_x64: Any) -> None:
        """Test activation script installation on Linux."""
        env_dir = tmp_path / "env"
        env_dir.mkdir()
        bin_dir = env_dir / "bin"
        bin_dir.mkdir()

        args = argparse.Namespace(bun="1.0.0", prompt=None, python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        # Check that activation scripts are created
        assert (bin_dir / "activate").exists()
        assert (bin_dir / "activate.fish").exists()
        assert (bin_dir / "shim").exists()

    def test_install_activate_windows(self, tmp_path: Any, mock_windows: Any) -> None:
        """Test activation script installation on Windows."""
        env_dir = tmp_path / "env"
        env_dir.mkdir()
        scripts_dir = env_dir / "Scripts"
        scripts_dir.mkdir()

        args = argparse.Namespace(bun="1.0.0", prompt=None, python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        # Check that activation scripts are created
        assert (scripts_dir / "activate.bat").exists()
        assert (scripts_dir / "deactivate.bat").exists()
        assert (scripts_dir / "Activate.ps1").exists()

    def test_install_activate_custom_prompt(self, tmp_path: Any, mock_linux_x64: Any) -> None:
        """Test custom prompt in activation scripts."""
        env_dir = tmp_path / "env"
        env_dir.mkdir()
        (env_dir / "bin").mkdir()

        custom_prompt = "(my-custom-env)"
        args = argparse.Namespace(bun="1.0.0", prompt=custom_prompt, python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        # Check that custom prompt is in activation script
        activate_file = env_dir / "bin" / "activate"
        content = activate_file.read_text()
        assert custom_prompt in content

    def test_install_activate_default_prompt(self, tmp_path: Any, mock_linux_x64: Any) -> None:
        """Test default prompt based on directory name."""
        env_dir = tmp_path / "my-bun-env"
        env_dir.mkdir()
        (env_dir / "bin").mkdir()

        args = argparse.Namespace(bun="1.0.0", prompt=None, python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        activate_file = env_dir / "bin" / "activate"
        content = activate_file.read_text()
        assert "(my-bun-env)" in content

    def test_install_activate_replaces_placeholders(self, tmp_path: Any, mock_linux_x64: Any) -> None:
        """Test that all placeholders are replaced in activation scripts."""
        env_dir = tmp_path / "env"
        env_dir.mkdir()
        (env_dir / "bin").mkdir()

        args = argparse.Namespace(bun="1.0.0", prompt=None, python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        activate_file = env_dir / "bin" / "activate"
        content = activate_file.read_text()

        # Check that placeholders are replaced
        assert "__BUN_VIRTUAL_PROMPT__" not in content
        assert "__BUN_VIRTUAL_ENV__" not in content
        assert "__SHIM_BUN__" not in content
        assert "__BIN_NAME__" not in content

    def test_install_activate_python_virtualenv_integration(self, tmp_path: Any, mock_linux_x64: Any) -> None:
        """Test activation script integration with Python virtualenv."""
        env_dir = tmp_path / "env"
        env_dir.mkdir()
        (env_dir / "bin").mkdir()

        args = argparse.Namespace(bun="1.0.0", prompt=None, python_virtualenv=True)

        bunenv.install_activate(str(env_dir), args)

        activate_file = env_dir / "bin" / "activate"
        content = activate_file.read_text()

        # Should have prompt disable/enable sections
        assert "BUN_VIRTUAL_ENV_DISABLE_PROMPT" in content

    def test_install_activate_system_bun(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test activation script with system bun."""
        import subprocess

        def fake_popen(*args: Any, **kwargs: Any) -> Any:
            class MockProc:
                def communicate(self) -> tuple[bytes, bytes]:
                    return (b"/usr/bin/bun\n", b"")

            return MockProc()

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        env_dir = tmp_path / "env"
        env_dir.mkdir()
        bin_dir = env_dir / "bin"
        bin_dir.mkdir()

        args = argparse.Namespace(bun="system", prompt=None, python_virtualenv=False)

        bunenv.install_activate(str(env_dir), args)

        # Should create shim pointing to system bun
        shim_file = bin_dir / "bun"
        assert shim_file.exists()


class TestSetPredeactivateHook:
    """Tests for set_predeactivate_hook function."""

    def test_set_predeactivate_hook_linux(self, tmp_path: Any, mock_linux_x64: Any) -> None:
        """Test predeactivate hook creation on Linux."""
        env_dir = tmp_path / "env"
        bin_dir = env_dir / "bin"
        bin_dir.mkdir(parents=True)

        bunenv.set_predeactivate_hook(str(env_dir))

        hook_file = bin_dir / "predeactivate"
        assert hook_file.exists()

        content = hook_file.read_text()
        assert "deactivate_bun" in content

    def test_set_predeactivate_hook_windows(self, tmp_path: Any, mock_windows: Any) -> None:
        """Test that predeactivate hook is not created on Windows."""
        env_dir = tmp_path / "env"
        env_dir.mkdir()

        bunenv.set_predeactivate_hook(str(env_dir))

        # Should not create anything on Windows
        assert not (env_dir / "Scripts" / "predeactivate").exists()


class TestCreateEnvironment:
    """Tests for create_environment function."""

    def test_create_environment_basic(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test basic environment creation."""

        def fake_install_bun(env_dir: str, src_dir: str, args: Any) -> None:
            # Create fake structure
            bin_dir = os.path.join(env_dir, "bin")
            os.makedirs(bin_dir, exist_ok=True)
            with open(os.path.join(bin_dir, "bun"), "w") as f:
                f.write("fake bun")

        monkeypatch.setattr(bunenv, "install_bun", fake_install_bun)
        monkeypatch.setattr(bunenv, "install_activate", lambda *args: None)

        env_dir = tmp_path / "test-env"

        args = argparse.Namespace(
            bun="1.0.0",
            python_virtualenv=False,
            force=False,
            requirements="",
            clean_src=False,
        )

        bunenv.create_environment(str(env_dir), args)

        assert env_dir.exists()
        assert (env_dir / "src").exists()

    def test_create_environment_existing_dir_no_force(self, tmp_path: Any) -> None:
        """Test that existing directory without --force causes exit."""
        env_dir = tmp_path / "existing-env"
        env_dir.mkdir()

        args = argparse.Namespace(bun="1.0.0", python_virtualenv=False, force=False, requirements="", clean_src=False)

        with pytest.raises(SystemExit):
            bunenv.create_environment(str(env_dir), args)

    def test_create_environment_existing_dir_with_force(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test that existing directory with --force continues."""
        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)
        monkeypatch.setattr(bunenv, "install_activate", lambda *args: None)

        env_dir = tmp_path / "existing-env"
        env_dir.mkdir()

        args = argparse.Namespace(bun="1.0.0", python_virtualenv=False, force=True, requirements="", clean_src=False)

        # Should not raise
        bunenv.create_environment(str(env_dir), args)

    def test_create_environment_clean_src(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test that src directory is cleaned when --clean-src is used."""
        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)
        monkeypatch.setattr(bunenv, "install_activate", lambda *args: None)

        env_dir = tmp_path / "test-env"

        args = argparse.Namespace(bun="1.0.0", python_virtualenv=False, force=False, requirements="", clean_src=True)

        bunenv.create_environment(str(env_dir), args)

        # src directory should be removed
        assert not (env_dir / "src").exists()

    def test_create_environment_with_requirements(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test environment creation with requirements file."""
        install_packages_called = False

        def fake_install_packages(env_dir: str, args: Any) -> None:
            nonlocal install_packages_called
            install_packages_called = True

        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)
        monkeypatch.setattr(bunenv, "install_activate", lambda *args: None)
        monkeypatch.setattr(bunenv, "install_packages", fake_install_packages)

        env_dir = tmp_path / "test-env"
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("package1\n")

        args = argparse.Namespace(
            bun="1.0.0",
            python_virtualenv=False,
            force=False,
            requirements=str(req_file),
            clean_src=False,
        )

        bunenv.create_environment(str(env_dir), args)

        assert install_packages_called

    def test_create_environment_python_virtualenv(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test environment creation with Python virtualenv integration."""
        predeactivate_called = False

        def fake_set_predeactivate(env_dir: str) -> None:
            nonlocal predeactivate_called
            predeactivate_called = True

        monkeypatch.setattr(bunenv, "install_bun", lambda *args: None)
        monkeypatch.setattr(bunenv, "install_activate", lambda *args: None)
        monkeypatch.setattr(bunenv, "set_predeactivate_hook", fake_set_predeactivate)

        env_dir = tmp_path / "test-env"

        args = argparse.Namespace(bun="1.0.0", python_virtualenv=True, force=True, requirements="", clean_src=False)

        bunenv.create_environment(str(env_dir), args)

        assert predeactivate_called

    def test_create_environment_system_bun(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mock_linux_x64: Any
    ) -> None:
        """Test environment creation with system bun."""
        monkeypatch.setattr(bunenv, "install_activate", lambda *args: None)

        env_dir = tmp_path / "test-env"

        args = argparse.Namespace(bun="system", python_virtualenv=False, force=False, requirements="", clean_src=False)

        bunenv.create_environment(str(env_dir), args)

        # Should create basic structure without installing bun
        assert (env_dir / "bin").exists()
        assert (env_dir / "install").exists()
        assert (env_dir / "install" / "cache").exists()


class TestActivationScriptContent:
    """Tests for activation script templates."""

    def test_activate_sh_template_has_deactivate_function(self) -> None:
        """Test that bash activation script has deactivate function."""
        assert "deactivate_bun" in bunenv.ACTIVATE_SH
        assert "function" not in bunenv.ACTIVATE_SH or "deactivate_bun ()" in bunenv.ACTIVATE_SH

    def test_activate_fish_template_has_deactivate_function(self) -> None:
        """Test that fish activation script has deactivate function."""
        assert "deactivate_bun" in bunenv.ACTIVATE_FISH

    def test_activate_bat_template_has_env_vars(self) -> None:
        """Test that Windows batch script sets environment variables."""
        assert "BUN_VIRTUAL_ENV" in bunenv.ACTIVATE_BAT
        assert "BUN_INSTALL" in bunenv.ACTIVATE_BAT

    def test_activate_ps1_template_has_deactivate_function(self) -> None:
        """Test that PowerShell script has deactivate function."""
        assert "deactivate" in bunenv.ACTIVATE_PS1

    def test_shim_template_executes_bun(self) -> None:
        """Test that shim template executes actual bun."""
        assert "exec" in bunenv.SHIM
        assert "__SHIM_BUN__" in bunenv.SHIM

    def test_predeactivate_template(self) -> None:
        """Test predeactivate hook template."""
        assert "deactivate_bun" in bunenv.PREDEACTIVATE_SH
