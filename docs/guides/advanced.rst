Advanced Topics
===============

This guide covers advanced bunenv features for power users, edge cases, and specialized scenarios.

Binary Variants Deep Dive
--------------------------

Understanding Bun's build variants helps you choose the right binary for your needs.

Standard vs Baseline
~~~~~~~~~~~~~~~~~~~~

Bun provides two main CPU optimization levels:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Variant
     - CPU Requirements
     - Performance
   * - **Standard** (default)
     - Modern CPUs (Haswell/Excavator, 2013+)
     - Optimized with AVX2, BMI2
   * - **Baseline**
     - Older CPUs (Nehalem/Bulldozer, 2008+)
     - Compatible but slower

Check your CPU support:

.. code-block:: bash

   # Linux
   grep -o 'avx2' /proc/cpuinfo | head -1

   # macOS
   sysctl -a | grep machdep.cpu.features | grep AVX2

If you see ``avx2``, use standard. Otherwise, use baseline.

**Example**:

.. code-block:: bash

   # Old server without AVX2
   bunenv .venv --variant=baseline

   # Modern laptop
   bunenv .venv  # Uses standard automatically

musl vs glibc (Linux)
~~~~~~~~~~~~~~~~~~~~~

Linux distributions use different C libraries:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Distribution
     - C Library
     - Variant Needed
   * - Alpine Linux
     - musl
     - ``musl`` (auto-detected)
   * - Void Linux
     - musl
     - ``musl`` (auto-detected)
   * - Ubuntu/Debian/Fedora/etc
     - glibc
     - Standard (default)

bunenv auto-detects musl, but you can force it:

.. code-block:: bash

   # Auto-detect (recommended)
   bunenv .venv

   # Force musl
   bunenv .venv --variant=musl

Check your system:

.. code-block:: bash

   ldd --version
   # Output contains "musl" or "GNU libc"

Profile Variant
~~~~~~~~~~~~~~~

The ``profile`` variant includes debug symbols and profiling support:

.. code-block:: bash

   bunenv .venv --variant=profile

**When to use**:
- Performance profiling
- Debugging Bun itself
- Contributing to Bun development

**Trade-offs**:
- Larger binary size
- Slower execution
- More memory usage

GitHub API Integration
----------------------

Understanding Rate Limits
~~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub API limits affect bunenv when listing versions:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Authentication
     - Requests/Hour
     - Sufficient For
   * - None
     - 60
     - Casual use
   * - With Token
     - 5,000
     - CI/CD, heavy use

Check your current limit:

.. code-block:: bash

   curl https://api.github.com/rate_limit

With token:

.. code-block:: bash

   curl -H "Authorization: token ghp_your_token" \
     https://api.github.com/rate_limit

Creating Minimal-Scope Tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For maximum security, create tokens with minimal permissions:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. **Expiration**: Choose appropriate lifetime
4. **Scopes**: None! (public repos only)
5. Copy token (``ghp_...``)

**Use it**:

.. code-block:: bash

   # Command line
   bunenv .venv --github-token=ghp_your_token

   # Environment variable (CI/CD)
   export GITHUB_TOKEN=ghp_your_token
   bunenv .venv --github-token=$GITHUB_TOKEN

   # Config file (local dev)
   echo "github_token = ghp_your_token" >> ~/.bunenvrc

.. important::
   The token only needs public repo access. Don't grant unnecessary permissions!

Using GitHub Enterprise or Mirrors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For organizations using GitHub Enterprise or mirrors:

.. code-block:: bash

   # GitHub Enterprise
   bunenv .venv --mirror=https://github.example.com/oven-sh/bun/releases

   # Local mirror
   bunenv .venv --mirror=https://artifacts.internal.com/bun/releases

The mirror must follow GitHub Releases URL structure:

.. code-block:: text

   {mirror}/bun-v{version}/bun-{platform}-{arch}[-{variant}].zip

Custom Activation Scripts
--------------------------

Understanding the Activation Mechanism
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you activate, bunenv modifies your shell environment:

.. code-block:: bash

   # Before activation
   $ which bun
   /usr/local/bin/bun  # System Bun (if installed)

   $ echo $PATH
   /usr/local/bin:/usr/bin:/bin

   # Activate
   $ source .venv/bin/activate

   # After activation
   (venv) $ which bun
   /path/to/.venv/bin/bun  # Environment Bun

   (venv) $ echo $PATH
   /path/to/.venv/bin:/usr/local/bin:/usr/bin:/bin  # Prepended!

The activation script:

1. Saves current ``PATH`` to ``_OLD_BUN_VIRTUAL_PATH``
2. Prepends environment's ``bin/`` to ``PATH``
3. Sets ``BUN_VIRTUAL_ENV``, ``BUN_INSTALL``, ``BUN_INSTALL_BIN``
4. Changes prompt (unless ``BUN_VIRTUAL_ENV_DISABLE_PROMPT=1``)

Customizing the Prompt
~~~~~~~~~~~~~~~~~~~~~~~

**Option 1: Custom prefix**

.. code-block:: bash

   bunenv .venv --prompt="[my-app] "
   source .venv/bin/activate
   [my-app] $

**Option 2: Disable prompt changes**

.. code-block:: bash

   export BUN_VIRTUAL_ENV_DISABLE_PROMPT=1
   source .venv/bin/activate
   $  # No prefix

**Option 3: Modify activation script**

.. code-block:: bash

   # After creating environment, edit:
   nano .venv/bin/activate

   # Find and modify this line:
   PS1="__BUN_VIRTUAL_PROMPT__ ${PS1:-}"

   # Change to your custom logic

Post-Activation Hooks
~~~~~~~~~~~~~~~~~~~~~

Run custom commands after activation:

.. code-block:: bash

   # .venv/bin/postactivate (create this file)
   #!/bin/bash
   echo "Welcome to my-app environment!"
   echo "Bun version: $(bun --version)"
   echo "Node modules: $(du -sh node_modules 2>/dev/null || echo 'none')"

Make it executable:

.. code-block:: bash

   chmod +x .venv/bin/postactivate

Then modify ``.venv/bin/activate``:

.. code-block:: bash

   # Add at end of activate script
   if [ -f "$BUN_VIRTUAL_ENV/bin/postactivate" ]; then
     . "$BUN_VIRTUAL_ENV/bin/postactivate"
   fi

Pre-Deactivation Hooks
~~~~~~~~~~~~~~~~~~~~~~~

Run cleanup before deactivating:

.. code-block:: bash

   # .venv/bin/predeactivate (automatically called on deactivate_bun)
   #!/bin/bash
   echo "Deactivating environment..."
   # Add cleanup logic here

Working with System Bun
-----------------------

The ``--bun=system`` Option
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of downloading Bun, create a shim to system Bun:

.. code-block:: bash

   # Requires Bun already installed
   bunenv .venv --bun=system
   source .venv/bin/activate

   (venv) $ which bun
   /path/to/.venv/bin/bun  # Shim that calls system Bun

**When to use**:
- You already have the correct Bun version installed
- Fast environment creation (no download)
- Shared Bun binary across environments (saves disk)

**Limitations**:
- Requires system Bun installed
- Not supported on Windows
- No version isolation (defeats the purpose of bunenv)

.. warning::
   Using ``system`` mode removes version isolation. Use specific versions for reproducibility!

Offline and Air-Gapped Installations
-------------------------------------

Pre-downloading Bun Binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For offline installations:

.. code-block:: bash

   # On connected machine, download Bun
   wget https://github.com/oven-sh/bun/releases/download/bun-v1.3.3/bun-linux-x64.zip

   # Transfer to offline machine
   scp bun-linux-x64.zip offline-machine:/tmp/

   # On offline machine, set up local mirror
   mkdir -p /opt/bun-mirror/bun-v1.3.3
   cp /tmp/bun-linux-x64.zip /opt/bun-mirror/bun-v1.3.3/

   # Start simple HTTP server
   cd /opt/bun-mirror
   python -m http.server 8000

   # Use mirror
   bunenv .venv --bun=1.3.3 --mirror=http://localhost:8000

Local Package Registry
~~~~~~~~~~~~~~~~~~~~~~~

Set up a local mirror for offline package installation:

.. code-block:: bash

   # Install Verdaccio (npm/Bun registry proxy)
   bun add -g verdaccio

   # Start it
   verdaccio

   # Configure Bun to use it
   bun config set registry http://localhost:4873

   # Now bun install works offline (for cached packages)

Integration with Other Tools
-----------------------------

Docker Integration
~~~~~~~~~~~~~~~~~~

Use bunenv during Docker builds for specific versions:

.. code-block:: dockerfile

   # Dockerfile
   FROM python:3.11-slim

   # Install bunenv
   RUN pip install bunenv

   # Create Bun environment
   RUN bunenv /opt/bunenv --bun=1.3.3 --clean-src

   # Add to PATH
   ENV PATH="/opt/bunenv/bin:${PATH}"

   # Now bun is available
   RUN bun --version

   WORKDIR /app
   COPY package.json bun.lockb ./
   RUN bun install

**When to use**:
- Multi-stage builds where you need specific Bun version
- Building from a Python base image
- Temporary Bun installation

**Alternatives**:
- Use official Bun Docker images for production: ``oven/bun:1.3.3``

Tox Integration
~~~~~~~~~~~~~~~

Use bunenv with tox for testing:

.. code-block:: ini

   # tox.ini
   [tox]
   envlist = py{310,311}-bun{1.2.0,1.3.0}

   [testenv]
   deps =
       bunenv
   commands_pre =
       bunenv {envtmpdir}/bunenv --bun={env:BUN_VERSION}
   commands =
       {envtmpdir}/bunenv/bin/bun test

   [testenv:py310-bun1.2.0]
   setenv = BUN_VERSION=1.2.0

   [testenv:py311-bun1.3.0]
   setenv = BUN_VERSION=1.3.0

Poetry Integration
~~~~~~~~~~~~~~~~~~

If using Poetry for Python deps:

.. code-block:: toml

   # pyproject.toml
   [tool.poetry.dependencies]
   python = "^3.10"
   bunenv = "^0.1.0"

   [tool.poetry.scripts]
   setup-bun = "scripts.setup:main"

.. code-block:: python

   # scripts/setup.py
   import subprocess
   import sys

   def main():
       """Setup Bun environment"""
       subprocess.run([
           sys.executable, "-m", "bunenv",
           ".venv-bun", "--bun=1.3.3", "--python-virtualenv"
       ])

Then:

.. code-block:: bash

   poetry install
   poetry run setup-bun
   poetry shell
   bun --version

Make Integration
~~~~~~~~~~~~~~~~

Add to Makefile:

.. code-block:: makefile

   # Makefile
   BUN_VERSION := 1.3.3
   BUN_ENV := .venv-bun

   .PHONY: setup-bun
   setup-bun:
       bunenv $(BUN_ENV) --bun=$(BUN_VERSION)
       @echo "Activate with: source $(BUN_ENV)/bin/activate"

   .PHONY: clean-bun
   clean-bun:
       rm -rf $(BUN_ENV)

   .PHONY: install-deps
   install-deps: setup-bun
       . $(BUN_ENV)/bin/activate && bun install

Security Considerations
-----------------------

SSL Certificate Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

bunenv verifies SSL certificates by default. Only disable if absolutely necessary:

.. code-block:: bash

   # UNSAFE - only for testing or corporate proxy
   bunenv .venv --ignore_ssl_certs

**Better alternatives**:

1. Add corporate CA to system trust store
2. Use internal mirror instead
3. Download binaries manually and use local mirror

Token Security
~~~~~~~~~~~~~~

Best practices for GitHub tokens:

**DO:**

✓ Use personal access tokens, not OAuth apps

✓ Set expiration dates

✓ Use environment variables in CI/CD

✓ Restrict to minimum scopes (none for public repos)

**DON'T:**

✗ Commit tokens to version control

✗ Share tokens between users

✗ Grant unnecessary permissions

✗ Use long-lived tokens without rotation

Verifying Downloaded Binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

bunenv downloads from official Bun GitHub releases, but you can verify:

.. code-block:: bash

   # After creating environment
   source .venv/bin/activate

   # Check Bun works
   bun --version

   # Check binary signature (if available)
   # Bun doesn't currently provide signatures, but check release notes

Multi-Architecture Scenarios
-----------------------------

Cross-Compilation Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

bunenv installs native binaries for your current architecture. For cross-platform work:

.. code-block:: bash

   # On macOS ARM (M1/M2)
   bunenv .venv-arm --bun=1.3.3  # ARM binary

   # For Rosetta/x64 compatibility
   arch -x86_64 bunenv .venv-x64 --bun=1.3.3  # x64 binary

   # Now you can test both:
   source .venv-arm/bin/activate && bun test
   deactivate_bun
   arch -x86_64 source .venv-x64/bin/activate && bun test

Fat Binaries (Future)
~~~~~~~~~~~~~~~~~~~~~

Bun doesn't currently provide universal binaries, but if they do:

.. code-block:: bash

   # Will automatically use universal binary when available
   bunenv .venv --bun=latest

Performance Optimization
------------------------

Speeding Up Environment Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use local mirrors**:

.. code-block:: bash

   # Cache downloads locally
   mkdir -p ~/.bun-cache
   bunenv .venv --mirror=file://$HOME/.bun-cache

**Skip source cleanup during dev**:

.. code-block:: bash

   # Keep source for reuse (faster subsequent installs)
   bunenv .venv  # Don't use --clean-src

**Use system Bun for temp environments**:

.. code-block:: bash

   # Fastest - no download
   bunenv .venv --bun=system

Disk Space Management
~~~~~~~~~~~~~~~~~~~~~

bunenv environments can use significant disk space:

.. code-block:: bash

   # Check size
   du -sh .venv
   # ~50MB per environment

**Optimization strategies**:

1. **Clean source after install**:

   .. code-block:: bash

      bunenv .venv --clean-src  # Saves ~50MB

2. **Share environments across projects** (carefully):

   .. code-block:: bash

      # Single shared environment
      bunenv ~/shared/bun-1.3.3 --bun=1.3.3

      # Symlink from projects
      ln -s ~/shared/bun-1.3.3 ~/project-a/.venv
      ln -s ~/shared/bun-1.3.3 ~/project-b/.venv

   .. warning::
      Sharing environments defeats isolation. Use with caution!

3. **Remove unused environments**:

   .. code-block:: bash

      # Find all bunenv environments
      find ~ -type f -name "bun" -path "*/.venv/bin/bun"

      # Remove old ones
      rm -rf old-project/.venv

Debugging and Introspection
----------------------------

Understanding Environment Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Peek inside an environment:

.. code-block:: bash

   tree .venv -L 2

   .venv/
   ├── bin/
   │   ├── activate
   │   ├── activate.fish
   │   ├── bun
   │   └── shim
   ├── install/         # Bun package cache
   │   └── cache/
   └── src/            # Downloaded files (if not cleaned)
       └── bun-linux-x64/

Inspecting Activation State
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # After activation
   source .venv/bin/activate

   # Check environment variables
   env | grep BUN
   # BUN_VIRTUAL_ENV=/path/to/.venv
   # BUN_INSTALL=/path/to/.venv
   # BUN_INSTALL_BIN=/path/to/.venv/bin

   # Check PATH modification
   echo $PATH | tr ':' '\n' | head -1
   # /path/to/.venv/bin

Verbose Mode for Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   bunenv .venv --verbose --bun=1.3.3

Shows:

- Configuration loading
- Version resolution
- Download URLs
- Extraction progress
- Installation steps

Edge Cases and Gotchas
-----------------------

Windows-Specific Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Path separators**:

.. code-block:: bat

   REM Windows uses backslash
   bunenv .venv --bun=1.3.3
   .venv\Scripts\activate.bat  REM Not forward slash!

**PowerShell execution policy**:

.. code-block:: powershell

   # May need to allow script execution
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

   # Then activate
   .venv\Scripts\Activate.ps1

**System Bun not supported**:

.. code-block:: bash

   # ERROR on Windows
   bunenv .venv --bun=system

Nested Environments
~~~~~~~~~~~~~~~~~~~

Don't activate bunenvs while inside another:

.. code-block:: bash

   # BAD
   source project-a/.venv/bin/activate
   (project-a) $ source ../project-b/.venv/bin/activate
   # Undefined behavior!

   # GOOD
   source project-a/.venv/bin/activate
   (project-a) $ deactivate_bun
   $ source project-b/.venv/bin/activate

Conflicting Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have Bun environment variables set:

.. code-block:: bash

   # Existing variables might conflict
   echo $BUN_INSTALL
   /opt/bun

   # bunenv will override them (after activation)
   source .venv/bin/activate
   (venv) $ echo $BUN_INSTALL
   /path/to/.venv

This is intentional! Activation saves old values and restores on deactivate.

Next Steps
----------

You now know advanced bunenv features. For practical application:

- :doc:`workflows` - Use advanced features in real scenarios
- :doc:`troubleshooting` - Fix issues when they arise
- :doc:`contributing` - Help improve bunenv

Have an advanced use case we didn't cover? `Open an issue <https://github.com/JacobCoffee/bunenv/issues>`_!
