API Reference
=============

Complete technical reference for the bunenv module.

.. note::
   Looking for command-line options? See :doc:`cli`.

Module Overview
---------------

bunenv is a single-module package providing Bun virtual environment functionality.
All code lives in ``src/bunenv/__init__.py``, following the architecture of nodeenv.

.. code-block:: python

   import bunenv

   # Entry point
   bunenv.main()  # Called by `bunenv` command

   # Get available versions
   versions = bunenv.get_bun_versions()

   # Parse version strings
   parsed = bunenv.parse_version("1.3.3")  # (1, 3, 3)

Quick Reference
---------------

Core Functions
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Purpose
   * - :func:`~bunenv.main`
     - Entry point for CLI
   * - :func:`~bunenv.create_environment`
     - Create Bun environment
   * - :func:`~bunenv.get_bun_versions`
     - List available Bun versions
   * - :func:`~bunenv.get_last_stable_bun_version`
     - Get latest stable version
   * - :func:`~bunenv.install_bun`
     - Download and install Bun binary

Module Constants
----------------

.. py:data:: bunenv_version
   :type: str
   :value: "0.1.0"

   Current version of bunenv.

   .. code-block:: python

      import bunenv
      print(bunenv.bunenv_version)  # "0.1.0"

.. py:data:: is_WIN
   :type: bool

   True if running on Windows platform.

   .. code-block:: python

      import bunenv
      if bunenv.is_WIN:
          print("Running on Windows")

.. py:data:: is_CYGWIN
   :type: bool

   True if running on Cygwin or MSYS.

   .. code-block:: python

      import bunenv
      if bunenv.is_CYGWIN:
          print("Running on Cygwin/MSYS")

.. py:data:: ignore_ssl_certs
   :type: bool
   :value: False

   Whether to ignore SSL certificate verification.

   Set to True when using ``--ignore_ssl_certs`` flag.

   .. warning::
      Setting this to True disables security verification!

Configuration
-------------

.. autoclass:: bunenv.Config
   :members:
   :undoc-members:
   :show-inheritance:

   Configuration class for bunenv defaults and settings.

   **Class Attributes:**

   .. py:attribute:: bun
      :type: str
      :value: "latest"
      :noindex:

      Default Bun version to install.

   .. py:attribute:: variant
      :type: str
      :value: ""
      :noindex:

      Default Bun variant (auto-detect if empty).

   .. py:attribute:: github_token
      :type: str | None
      :value: None
      :noindex:

      GitHub personal access token for API requests.

   .. py:attribute:: prebuilt
      :type: bool
      :value: True
      :noindex:

      Always True for Bun (no source builds).

   .. py:attribute:: ignore_ssl_certs
      :type: bool
      :value: False
      :noindex:

      Whether to ignore SSL certificate verification.

   .. py:attribute:: mirror
      :type: str | None
      :value: None
      :noindex:

      Alternative mirror URL for downloads.

   **Example:**

   .. code-block:: python

      from bunenv import Config

      # Load from config files
      Config._load(["~/.bunenvrc"], verbose=True)

      # Access config
      print(Config.bun)  # "latest"
      print(Config.variant)  # ""

Environment Creation
--------------------

.. autofunction:: bunenv.create_environment

   Create a new Bun virtual environment.

   This is the main function that orchestrates environment creation:

   1. Creates directory structure
   2. Downloads and installs Bun binary
   3. Installs activation scripts
   4. Optionally installs packages from requirements file

   **Example:**

   .. code-block:: python

      import argparse
      from bunenv import create_environment

      # Create args namespace
      args = argparse.Namespace(
          bun="1.3.3",
          variant="",
          python_virtualenv=False,
          requirements="",
          clean_src=False,
          force=False,
          verbose=False,
          mirror=None,
          github_token=None,
      )

      # Create environment
      create_environment("/tmp/myenv", args)

.. autofunction:: bunenv.get_env_dir

   Get environment directory from arguments.

   Determines the target directory based on whether using Python virtualenv
   or explicit directory.

   **Example:**

   .. code-block:: python

      from bunenv import get_env_dir
      import argparse

      args = argparse.Namespace(
          python_virtualenv=False,
          env_dir="/tmp/myenv"
      )

      env_dir = get_env_dir(args)  # "/tmp/myenv"

Version Management
------------------

.. autofunction:: bunenv.get_bun_versions

   Return list of all available Bun versions from GitHub Releases.

   **Returns:**
      List of version strings (e.g., ``['1.3.3', '1.3.2', ...]``)

   **Example:**

   .. code-block:: python

      from bunenv import get_bun_versions

      versions = get_bun_versions()
      print(f"Available versions: {len(versions)}")
      print(f"Latest: {versions[0]}")
      print(f"First 10: {versions[:10]}")

   .. note::
      This makes an API request to GitHub. Use a token to avoid rate limits.

.. autofunction:: bunenv.get_last_stable_bun_version

   Return the most recent stable Bun version.

   **Returns:**
      Version string (e.g., ``"1.3.3"``) or None if fetch fails

   **Example:**

   .. code-block:: python

      from bunenv import get_last_stable_bun_version

      latest = get_last_stable_bun_version()
      print(f"Latest Bun: {latest}")

.. autofunction:: bunenv.print_bun_versions

   Print all available Bun versions to stdout.

   Formats output in columns of 8 versions each.

   **Example:**

   .. code-block:: python

      from bunenv import print_bun_versions

      print_bun_versions()
      # Output:
      # 1.3.3    1.3.2    1.3.1    1.3.0    1.2.15   1.2.14   1.2.13   1.2.12
      # ...

.. autofunction:: bunenv.parse_version

   Parse version string to tuple of integers.

   Handles common prefixes (``v``, ``bun-v``).

   **Args:**
      version_str: Version string to parse

   **Returns:**
      Tuple of integers (e.g., ``(1, 3, 3)``) or empty tuple if invalid

   **Example:**

   .. code-block:: python

      from bunenv import parse_version

      assert parse_version("1.3.3") == (1, 3, 3)
      assert parse_version("v1.3.3") == (1, 3, 3)
      assert parse_version("bun-v1.3.3") == (1, 3, 3)
      assert parse_version("invalid") == ()

.. autofunction:: bunenv.bun_version_from_args

   Parse Bun version from argparse arguments.

   Handles both explicit versions and ``system`` Bun detection.

   **Example:**

   .. code-block:: python

      from bunenv import bun_version_from_args
      import argparse

      args = argparse.Namespace(bun="1.3.3")
      version = bun_version_from_args(args)
      # (1, 3, 3)

Binary Management
-----------------

.. autofunction:: bunenv.get_bun_bin_url

   Construct GitHub releases URL for Bun binary.

   Detects platform and architecture automatically, builds appropriate URL.

   **Args:**
      version: Bun version (e.g., "1.3.3")
      variant: Bun variant ("", "baseline", "musl", "profile")
      mirror: Alternative mirror URL (optional)

   **Returns:**
      Complete URL to download binary

   **Example:**

   .. code-block:: python

      from bunenv import get_bun_bin_url

      # Auto-detect platform/arch
      url = get_bun_bin_url("1.3.3")
      # "https://github.com/oven-sh/bun/releases/download/bun-v1.3.3/bun-linux-x64.zip"

      # With variant
      url = get_bun_bin_url("1.3.3", variant="baseline")
      # "https://github.com/oven-sh/bun/releases/download/bun-v1.3.3/bun-linux-x64-baseline.zip"

      # With mirror
      url = get_bun_bin_url("1.3.3", mirror="https://mirror.example.com")
      # "https://mirror.example.com/bun-v1.3.3/bun-linux-x64.zip"

.. autofunction:: bunenv.download_bun_bin

   Download Bun binary zip file from GitHub Releases.

   **Args:**
      bun_url: Complete URL to binary
      src_dir: Directory to extract to
      args: Argument namespace

   **Example:**

   .. code-block:: python

      from bunenv import get_bun_bin_url, download_bun_bin
      import argparse

      url = get_bun_bin_url("1.3.3")
      args = argparse.Namespace(verbose=True)

      download_bun_bin(url, "/tmp/src", args)
      # Downloads and extracts to /tmp/src/

.. autofunction:: bunenv.copy_bun_from_prebuilt

   Copy prebuilt Bun binary from extracted archive to environment.

   **Args:**
      env_dir: Environment directory
      src_dir: Source directory with extracted files
      bun_version: Bun version being installed

   **Example:**

   .. code-block:: python

      from bunenv import copy_bun_from_prebuilt

      copy_bun_from_prebuilt(
          env_dir="/tmp/myenv",
          src_dir="/tmp/src",
          bun_version="1.3.3"
      )
      # Copies to /tmp/myenv/bin/bun

Installation Functions
----------------------

.. autofunction:: bunenv.install_bun

   Download Bun binary and install it in virtual environment.

   High-level wrapper that handles download, extraction, and installation.

   **Args:**
      env_dir: Environment directory
      src_dir: Source/download directory
      args: Argument namespace

   **Example:**

   .. code-block:: python

      from bunenv import install_bun
      import argparse

      args = argparse.Namespace(
          bun="1.3.3",
          variant="",
          mirror=None,
          verbose=True
      )

      install_bun("/tmp/myenv", "/tmp/src", args)

.. autofunction:: bunenv.install_bun_wrapped

   Internal wrapper for install_bun with error handling.

   .. note::
      Use :func:`install_bun` instead - it provides better error handling.

.. autofunction:: bunenv.install_packages

   Install packages via bun add -g.

   Reads packages from requirements file and installs them globally in the environment.

   **Args:**
      env_dir: Environment directory
      args: Must have ``requirements`` attribute with file path

   **Example:**

   .. code-block:: python

      from bunenv import install_packages
      import argparse

      args = argparse.Namespace(
          requirements="requirements-bun.txt",
          verbose=True
      )

      install_packages("/tmp/myenv", args)

Activation Scripts
------------------

.. autofunction:: bunenv.install_activate

   Install virtual environment activation scripts.

   Creates platform-appropriate activation scripts in the environment.

   **Unix**: ``activate`` (bash/zsh), ``activate.fish``

   **Windows**: ``activate.bat``, ``Activate.ps1``

   **Args:**
      env_dir: Environment directory
      args: Argument namespace

   **Example:**

   .. code-block:: python

      from bunenv import install_activate
      import argparse

      args = argparse.Namespace(
          bun="1.3.3",
          prompt="",
          python_virtualenv=False
      )

      install_activate("/tmp/myenv", args)

.. autofunction:: bunenv.set_predeactivate_hook

   Set pre-deactivation hook for Python virtualenv integration.

   Creates a hook that deactivates Bun environment before deactivating Python virtualenv.

   **Args:**
      env_dir: Environment directory

   **Example:**

   .. code-block:: python

      from bunenv import set_predeactivate_hook

      set_predeactivate_hook("/tmp/myenv")

Command-Line Interface
----------------------

.. autofunction:: bunenv.make_parser

   Create argument parser for bunenv CLI.

   **Returns:**
      Configured ArgumentParser instance

   **Example:**

   .. code-block:: python

      from bunenv import make_parser

      parser = make_parser()
      args = parser.parse_args(["myenv", "--bun=1.3.3"])

.. autofunction:: bunenv.parse_args

   Parse command-line arguments with validation.

   **Args:**
      check: Whether to validate arguments (default True)

   **Returns:**
      Parsed argument namespace

   **Example:**

   .. code-block:: python

      from bunenv import parse_args
      import sys

      # Temporarily replace sys.argv
      sys.argv = ["bunenv", "myenv", "--bun=1.3.3"]
      args = parse_args()

      print(args.env_dir)  # "myenv"
      print(args.bun)  # "1.3.3"

.. autofunction:: bunenv.main

   Main entry point for bunenv CLI.

   Called when you run ``bunenv`` command.

   **Example:**

   .. code-block:: python

      import sys
      from bunenv import main

      # Run programmatically
      sys.argv = ["bunenv", "--list"]
      main()

Utility Functions
-----------------

File System
~~~~~~~~~~~

.. autofunction:: bunenv.mkdir

   Create directory with logging.

   **Args:**
      path: Directory path to create

   **Example:**

   .. code-block:: python

      from bunenv import mkdir

      mkdir("/tmp/test/nested/dir")

.. autofunction:: bunenv.writefile

   Create file and write content with executable permissions.

   **Args:**
      dest: Destination file path
      content: Content to write (str or bytes)
      overwrite: Whether to overwrite existing (default True)
      append: Whether to append to existing (default False)

   **Example:**

   .. code-block:: python

      from bunenv import writefile

      writefile("/tmp/script.sh", "#!/bin/bash\necho Hello")
      # Creates executable file

.. autofunction:: bunenv.make_executable

   Make file executable (Unix mode 0755).

   **Args:**
      filename: File to make executable

   **Example:**

   .. code-block:: python

      from bunenv import make_executable

      make_executable("/tmp/script.sh")

String Processing
~~~~~~~~~~~~~~~~~

.. autofunction:: bunenv.clear_output

   Remove newlines and decode bytes to string.

   **Args:**
      out: Bytes output from subprocess

   **Returns:**
      Cleaned string

   **Example:**

   .. code-block:: python

      from bunenv import clear_output

      output = b"1.3.3\n"
      clean = clear_output(output)  # "1.3.3"

.. autofunction:: bunenv.remove_env_bin_from_path

   Remove environment's bin directory from PATH string.

   **Args:**
      env: PATH environment variable
      env_bin_dir: Bin directory to remove

   **Returns:**
      Modified PATH string

   **Example:**

   .. code-block:: python

      from bunenv import remove_env_bin_from_path

      path = "/tmp/myenv/bin:/usr/bin:/bin"
      clean = remove_env_bin_from_path(path, "/tmp/myenv/bin")
      # ":/usr/bin:/bin"

System Detection
~~~~~~~~~~~~~~~~

.. autofunction:: bunenv.is_x86_64_musl

   Check if running on musl libc (Alpine Linux, Void Linux).

   **Returns:**
      True if musl detected

   **Example:**

   .. code-block:: python

      from bunenv import is_x86_64_musl

      if is_x86_64_musl():
          print("Use musl variant")

Process Execution
~~~~~~~~~~~~~~~~~

.. autofunction:: bunenv.callit

   Execute command in subprocess with logging.

   **Args:**
      cmd: Command list or string
      show_stdout: Whether to show output (default True)
      in_shell: Run in shell (default False)
      cwd: Working directory (optional)
      extra_env: Additional environment variables (optional)

   **Returns:**
      Tuple of (return_code, output_lines)

   **Example:**

   .. code-block:: python

      from bunenv import callit

      returncode, output = callit(
          ["bun", "--version"],
          show_stdout=True
      )

Network
~~~~~~~

.. autofunction:: bunenv.urlopen

   Open URL with custom headers and SSL handling.

   Automatically adds User-Agent and GitHub token if configured.

   **Args:**
      url: URL to open

   **Returns:**
      urllib response object

   **Example:**

   .. code-block:: python

      from bunenv import urlopen

      response = urlopen("https://api.github.com/repos/oven-sh/bun/releases")
      data = response.read()

.. autofunction:: bunenv.zipfile_open

   Context manager for safe zipfile handling.

   **Example:**

   .. code-block:: python

      from bunenv import zipfile_open

      with zipfile_open("archive.zip", "r") as zf:
          zf.extractall("/tmp/extracted")

Logging
~~~~~~~

.. autofunction:: bunenv.create_logger

   Create logger for diagnostic output.

   **Returns:**
      Configured Logger instance

   **Example:**

   .. code-block:: python

      from bunenv import create_logger

      logger = create_logger()
      logger.info("Installing Bun...")

Shell Script Templates
----------------------

bunenv includes shell script templates for activation:

.. py:data:: ACTIVATE_SH
   :type: str

   Bash/zsh activation script template.

.. py:data:: ACTIVATE_FISH
   :type: str

   Fish shell activation script template.

.. py:data:: ACTIVATE_BAT
   :type: str

   Windows cmd.exe activation script template.

.. py:data:: ACTIVATE_PS1
   :type: str

   Windows PowerShell activation script template.

.. py:data:: DEACTIVATE_BAT
   :type: str

   Windows cmd.exe deactivation script template.

.. py:data:: SHIM
   :type: str

   System Bun wrapper script template.

.. py:data:: PREDEACTIVATE_SH
   :type: str

   Pre-deactivation hook for Python virtualenv.

These templates are populated with environment-specific values during installation.

See Also
--------

- :doc:`cli` - Command-line interface reference
- :doc:`../guides/advanced` - Advanced usage patterns
- Source code: https://github.com/JacobCoffee/bunenv

Index and Search
----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
