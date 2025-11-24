bunenv - Bun Virtual Environment Builder
=========================================

.. image:: https://badge.fury.io/py/bunenv.svg
   :target: https://badge.fury.io/py/bunenv
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/bunenv.svg
   :target: https://pypi.org/project/bunenv/
   :alt: Python Versions

.. image:: https://img.shields.io/badge/license-BSD--3--Clause-blue.svg
   :target: https://github.com/JacobCoffee/bunenv/blob/main/LICENSE
   :alt: License

**bunenv** creates isolated `Bun <https://bun.sh>`_ environments, just like virtualenv does for Python.

Think of it as your workspace manager for Bun - each project gets its own sandbox with the exact Bun version it needs,
without interfering with other projects or your system installation.

Why bunenv?
-----------

Have you ever needed to:

- Test your code against multiple Bun versions?
- Keep project dependencies isolated from each other?
- Use a specific Bun version without changing your system installation?
- Integrate Bun into Python-based workflows?

**bunenv solves all of these.** It's virtualenv for Bun.

.. note::
   bunenv is adapted from the excellent `nodeenv <https://github.com/ekalinin/nodeenv>`_ project,
   bringing proven environment isolation techniques to the Bun.js ecosystem.

Quick Start: 60 Seconds to Your First Environment
--------------------------------------------------

Install bunenv:

.. code-block:: bash

   pip install bunenv

Create and activate a Bun environment:

.. code-block:: bash

   # Create environment with latest Bun
   bunenv my-project

   # Activate it (macOS/Linux)
   source my-project/bin/activate

   # Now you have an isolated Bun!
   bun --version
   bun init
   bun install express

When you're done:

.. code-block:: bash

   deactivate_bun

That's it! You now have a completely isolated Bun environment.

Key Features
------------

Zero Dependencies
    Pure Python stdlib - no external packages required

Cross-Platform Support
    Works seamlessly on macOS (Intel & Apple Silicon), Linux (glibc & musl), and Windows

Version Flexibility
    Install any Bun version from GitHub Releases - latest, specific versions, or system Bun

Python Integration
    Create Bun environments inside Python virtualenvs for polyglot projects

Smart Defaults
    Automatic architecture detection, variant selection, and platform handling

Multiple Shell Support
    Activation scripts for bash, zsh, fish, PowerShell, and cmd.exe

What Makes bunenv Different?
-----------------------------

Compared to nodeenv
~~~~~~~~~~~~~~~~~~~

While bunenv is inspired by nodeenv, it's tailored for Bun's unique architecture:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - nodeenv
     - bunenv
   * - Runtime
     - Node.js
     - Bun
   * - Package Manager
     - npm (separate binary)
     - Built into Bun
   * - Version Source
     - nodejs.org index.json
     - GitHub Releases API
   * - Source Builds
     - Supported
     - Not available (prebuilt only)
   * - Architecture
     - Standard naming
     - aarch64 for ARM

Compared to Other Version Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Feature
     - bunenv
     - asdf
     - mise
     - Homebrew
   * - Isolated Envs
     - ✓
     - Limited
     - Limited
     - ✗
   * - Multiple Versions
     - ✓
     - ✓
     - ✓
     - Limited
   * - Python Integration
     - ✓
     - ✗
     - ✗
     - ✗
   * - Zero Config
     - ✓
     - ✗
     - ✗
     - ✓
   * - No Shell Hooks
     - ✓
     - ✗
     - ✗
     - N/A

Real-World Example
------------------

The `Byte Bot <https://github.com/JacobCoffee/byte>`_ project uses bunenv to manage Bun for frontend tooling
(TailwindCSS, Biome) alongside Python (uv) for the backend:

.. code-block:: bash

   # Setup isolated Bun environment
   bunenv .bunenv --bun=latest
   source .bunenv/bin/activate

   # Frontend development with isolated tools
   bun install          # Install dependencies
   bun run format       # Biome formatting
   bun run lint         # Biome linting
   bun run build        # Build assets

This keeps frontend tooling completely separate from system installations and other projects.

When to Use bunenv
------------------

Perfect For
~~~~~~~~~~~

✓ **Development**: Test against multiple Bun versions

✓ **CI/CD**: Reproducible builds with pinned versions

✓ **Teaching**: Give students isolated environments

✓ **Polyglot Projects**: Python backend + Bun frontend

✓ **Legacy Projects**: Keep old projects on old Bun versions

Maybe Not For
~~~~~~~~~~~~~

✗ **Production Deployments**: Use Docker or official Bun installation

✗ **Global Tools**: System Bun is fine for personal scripts

✗ **Single Version Setup**: Native Bun install is simpler

Getting Started
---------------

Ready to dive in? Here's your learning path:

.. card:: 🚀 New to bunenv?

   Start with the :doc:`guides/quickstart` tutorial - you'll have your first environment
   running in 5 minutes.

.. card:: 📚 Need specifics?

   Check the :doc:`guides/index` for task-oriented guides on common workflows.

.. card:: 🔧 Looking for details?

   The :doc:`api/index` has complete technical reference for all functions and options.

.. card:: 🤝 Want to contribute?

   See :doc:`guides/contributing` for development setup and guidelines.

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Tutorials & Guides

   guides/quickstart
   guides/index
   guides/workflows
   guides/configuration
   guides/advanced
   guides/troubleshooting
   guides/contributing

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api/index
   api/cli

.. toctree::
   :maxdepth: 1
   :caption: About

   guides/comparison
   guides/migrating

Platform Support
----------------

Supported Operating Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **macOS**: Intel (x64), Apple Silicon (aarch64)
- **Linux**: x64 and aarch64, both glibc and musl (Alpine, Void)
- **Windows**: x64 (baseline and standard variants)

Supported Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Python 3.10+
- CPython and PyPy implementations

Supported Shells
~~~~~~~~~~~~~~~~

- **Unix**: bash, zsh, fish, csh/tcsh
- **Windows**: PowerShell, cmd.exe, Git Bash (via MSYS2)

Quick Reference
---------------

Common Commands
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create environment
   bunenv myenv                          # Latest Bun
   bunenv myenv --bun=1.3.3             # Specific version
   bunenv myenv --variant=baseline      # Older CPU support

   # List available versions
   bunenv --list

   # Activate (macOS/Linux)
   source myenv/bin/activate

   # Activate (Windows)
   myenv\Scripts\activate.bat           # cmd.exe
   myenv\Scripts\Activate.ps1           # PowerShell

   # Use Bun
   bun --version
   bun add express

   # Deactivate
   deactivate_bun

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

When activated, bunenv sets:

- ``BUN_VIRTUAL_ENV`` - Path to the environment
- ``BUN_INSTALL`` - Bun installation directory
- ``BUN_INSTALL_BIN`` - Binary directory
- ``PATH`` - Prepended with environment's bin directory

Configuration File
~~~~~~~~~~~~~~~~~~

Create ``~/.bunenvrc`` for defaults:

.. code-block:: ini

   [bunenv]
   bun = latest
   github_token = ghp_your_token_here
   variant =
   ignore_ssl_certs = False

Or use ``.bun-version`` in your project:

.. code-block:: bash

   echo "1.3.3" > .bun-version
   bunenv .venv  # Uses version from file

Get Help
--------

Having trouble? We're here to help:

📖 **Documentation Issues**: Check :doc:`guides/troubleshooting`

🐛 **Bug Reports**: `GitHub Issues <https://github.com/JacobCoffee/bunenv/issues>`_

💬 **Questions**: Open a `GitHub Discussion <https://github.com/JacobCoffee/bunenv/discussions>`_

🔍 **Search**: Use the search box at the top of this page

Links & Resources
-----------------

Project Links
~~~~~~~~~~~~~

- **PyPI**: https://pypi.org/project/bunenv/
- **GitHub**: https://github.com/JacobCoffee/bunenv
- **Issues**: https://github.com/JacobCoffee/bunenv/issues
- **Changelog**: https://github.com/JacobCoffee/bunenv/releases

External Resources
~~~~~~~~~~~~~~~~~~

- **Bun Documentation**: https://bun.sh/docs
- **Bun GitHub**: https://github.com/oven-sh/bun
- **nodeenv** (inspiration): https://github.com/ekalinin/nodeenv

Project Information
-------------------

:Version: |version|
:License: BSD-3-Clause
:Python: 3.10+
:Author: Jacob Coffee
:Source: https://github.com/JacobCoffee/bunenv

Credits
-------

bunenv is adapted from `nodeenv <https://github.com/ekalinin/nodeenv>`_ by Eugene Kalinin.

Special thanks to:

- **Eugene Kalinin** - Original nodeenv author and maintainer
- **Oven.sh Team** - For creating Bun
- **All Contributors** - For improvements and bug reports

The nodeenv project provided an excellent foundation for environment isolation,
and bunenv builds on that proven architecture for the Bun ecosystem.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
