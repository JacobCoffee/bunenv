Comparison with Other Tools
============================

Understanding how bunenv compares to other tools helps you choose the right solution for your needs.

bunenv vs nodeenv
-----------------

bunenv is directly adapted from `nodeenv <https://github.com/ekalinin/nodeenv>`_, bringing the same
proven architecture to the Bun ecosystem.

Similarities
~~~~~~~~~~~~

Both tools share the same core philosophy:

- **Isolated environments**: Keep projects separate
- **Version management**: Multiple versions on one machine
- **Activation scripts**: Similar shell integration
- **Python integration**: Work inside Python virtualenvs
- **Zero config**: Work out of the box with sensible defaults

Key Differences
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - nodeenv
     - bunenv
   * - **Runtime**
     - Node.js
     - Bun
   * - **Package Manager**
     - npm (separate binary)
     - Built into Bun (all-in-one)
   * - **Version Source**
     - nodejs.org index.json
     - GitHub Releases API
   * - **Source Builds**
     - Supported
     - Not available (prebuilt only)
   * - **LTS Support**
     - Yes (Node.js LTS)
     - Not yet (Bun doesn't have LTS)
   * - **Architecture Names**
     - Standard (x64, arm64)
     - Bun-specific (aarch64 for ARM)
   * - **Environment Variables**
     - NODE_PATH, NPM_CONFIG_PREFIX
     - BUN_INSTALL, BUN_INSTALL_BIN
   * - **Maturity**
     - Stable, 10+ years
     - New, based on nodeenv

When to Choose bunenv over nodeenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose **bunenv** if you:

✓ Use Bun for your JavaScript runtime

✓ Want all-in-one tooling (runtime + package manager + bundler)

✓ Need faster package installation

✓ Work with Bun-specific features

Choose **nodeenv** if you:

✓ Use Node.js or npm-specific features

✓ Need LTS version support

✓ Require source builds from git

✓ Have established Node.js tooling

bunenv vs asdf
--------------

`asdf <https://asdf-vm.com/>`_ is a multi-runtime version manager supporting Node, Ruby, Python, and more.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - asdf
     - bunenv
   * - **Isolation**
     - Version switching, not full isolation
     - Fully isolated environments
   * - **Multiple Versions**
     - One active at a time (global/local)
     - Multiple active simultaneously
   * - **Shell Integration**
     - Required (shell hooks)
     - Optional (activation scripts)
   * - **Language Support**
     - Many runtimes via plugins
     - Bun only
   * - **Python Integration**
     - Separate tools
     - Native (install in virtualenv)
   * - **Setup Complexity**
     - Plugin installation required
     - Zero configuration
   * - **Dependencies**
     - Shell-dependent
     - Python only

Practical Comparison
~~~~~~~~~~~~~~~~~~~~

**asdf**:

.. code-block:: bash

   # Global version
   asdf install bun latest
   asdf global bun latest

   # Per-project version
   cd project
   echo "1.3.3" > .tool-versions
   asdf install bun 1.3.3
   asdf local bun 1.3.3

**bunenv**:

.. code-block:: bash

   # Per-project environment
   cd project
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate

   # Multiple projects active simultaneously
   cd ../other-project
   bunenv .venv --bun=1.0.0
   source .venv/bin/activate  # Doesn't affect first project

When to Choose bunenv over asdf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose **bunenv** if you:

✓ Need true isolation (not just version switching)

✓ Want multiple Bun versions active simultaneously

✓ Use Python + Bun together

✓ Prefer activation over global version files

✓ Don't want shell-level integration

Choose **asdf** if you:

✓ Manage multiple language runtimes

✓ Prefer global version management

✓ Want per-directory automatic switching

✓ Use the asdf ecosystem

bunenv vs mise
--------------

`mise <https://mise.jdx.dev/>`_ (formerly rtx) is a modern asdf alternative written in Rust.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - mise
     - bunenv
   * - **Isolation**
     - Version switching
     - Full environment isolation
   * - **Performance**
     - Very fast (Rust)
     - Fast (Python)
   * - **Configuration**
     - .mise.toml, .tool-versions
     - .bun-version, .bunenvrc
   * - **Task Runner**
     - Yes (built-in)
     - No (use Bun's task runner)
   * - **Environment Variables**
     - Advanced (mise.toml)
     - Basic (activation scripts)
   * - **Python Integration**
     - Can manage Python
     - Works *with* Python

When to Choose bunenv over mise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose **bunenv** if you:

✓ Need true isolation per project

✓ Work in Python-centric workflows

✓ Want environments portable across machines

✓ Prefer explicit activation

Choose **mise** if you:

✓ Manage multiple languages

✓ Want automatic version switching

✓ Use mise's task runner

✓ Need advanced environment variable management

bunenv vs Homebrew/apt/System Install
--------------------------------------

System package managers install Bun globally.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - System Install
     - bunenv
   * - **Isolation**
     - None (global)
     - Full per-project
   * - **Multiple Versions**
     - One only
     - Unlimited
   * - **Setup Time**
     - Fastest
     - Quick (~30 seconds)
   * - **Disk Usage**
     - ~50MB total
     - ~50MB per environment
   * - **Updates**
     - System package manager
     - Per environment
   * - **Reproducibility**
     - System-dependent
     - Environment-specific

Practical Comparison
~~~~~~~~~~~~~~~~~~~~

**System Install** (Homebrew):

.. code-block:: bash

   # Install
   brew install bun

   # All projects use same version
   cd project-a && bun --version  # 1.3.3
   cd project-b && bun --version  # 1.3.3

   # Upgrading affects all projects
   brew upgrade bun

**bunenv**:

.. code-block:: bash

   # Install per project
   cd project-a
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun --version  # 1.3.3

   cd ../project-b
   bunenv .venv --bun=1.0.0
   source .venv/bin/activate
   bun --version  # 1.0.0

When to Use System Install
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose **system install** if you:

✓ Only use one Bun version

✓ Don't need version isolation

✓ Use Bun for personal scripts/tools

✓ Want simplest possible setup

Choose **bunenv** if you:

✓ Maintain multiple projects

✓ Need different Bun versions

✓ Want reproducible environments

✓ Collaborate with teams

bunenv vs Docker
----------------

Docker provides complete environment isolation.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - Docker
     - bunenv
   * - **Isolation**
     - Complete (containers)
     - Process (environment)
   * - **Overhead**
     - High (virtualization)
     - Minimal (local binary)
   * - **Speed**
     - Slower (container startup)
     - Fast (native execution)
   * - **Production Parity**
     - Excellent
     - Moderate
   * - **Complexity**
     - Higher (Dockerfile, etc.)
     - Lower (one command)
   * - **Disk Usage**
     - Large (full images)
     - Small (Bun only)

Practical Comparison
~~~~~~~~~~~~~~~~~~~~

**Docker**:

.. code-block:: bash

   # Dockerfile
   FROM oven/bun:1.3.3
   WORKDIR /app
   COPY package.json bun.lockb ./
   RUN bun install
   COPY . .
   CMD ["bun", "run", "start"]

   # Build and run
   docker build -t myapp .
   docker run -p 3000:3000 myapp

**bunenv**:

.. code-block:: bash

   # Local development
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun install
   bun run start

Combined Approach
~~~~~~~~~~~~~~~~~

Use **both** for optimal workflow:

.. code-block:: bash

   # Development: bunenv (fast iteration)
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun run dev

   # Production: Docker (consistency)
   docker build -t myapp .
   docker run myapp

This gives you fast local development with production parity for deployment.

bunenv vs Official Bun Installer
---------------------------------

Bun's official installer (``curl -fsSL https://bun.sh/install | bash``) installs system-wide.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - Official Installer
     - bunenv
   * - **Installation**
     - Shell script
     - Python package
   * - **Version Management**
     - Upgrades in-place
     - Multiple isolated versions
   * - **Scope**
     - User-level (~/.bun)
     - Project-level (.venv)
   * - **Dependencies**
     - None
     - Python 3.10+
   * - **CI/CD**
     - GitHub Actions available
     - Python-based workflows

When to Use Official Installer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose **official installer** if you:

✓ Want official Bun installation method

✓ Only need one Bun version

✓ Don't use Python tooling

✓ Want minimal dependencies

Choose **bunenv** if you:

✓ Maintain multiple projects with different versions

✓ Use Python-based development workflows

✓ Need project-specific isolation

✓ Want version pinning per project

Summary Matrix
--------------

Quick decision guide:

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Use Case
     - Best Tool
     - Alternative
     - Notes
   * - **Single project, one Bun version**
     - System install
     - Official installer
     - Simplest approach
   * - **Multiple projects, different versions**
     - bunenv
     - asdf/mise
     - True isolation
   * - **Python + Bun integration**
     - bunenv
     - Manual setup
     - Native integration
   * - **Multi-language version management**
     - asdf/mise
     - bunenv + pyenv
     - Broader scope
   * - **Production deployments**
     - Docker
     - System install
     - Containerization
   * - **CI/CD workflows**
     - bunenv
     - GitHub Actions
     - Reproducible builds
   * - **Teaching/workshops**
     - bunenv
     - Docker
     - Easy setup
   * - **Testing multiple Bun versions**
     - bunenv
     - Docker matrix
     - Parallel testing

Real-World Scenarios
--------------------

Scenario 1: Polyglot Full-Stack Developer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Needs**: Python backend + Bun frontend

**Best solution**: **bunenv**

.. code-block:: bash

   # Python virtualenv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # Add Bun to same environment
   pip install bunenv
   bunenv --python-virtualenv --bun=1.3.3

   # Both tools in one environment
   python manage.py runserver &
   bun run dev

Scenario 2: Multi-Service Monorepo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Needs**: Different services with different Bun versions

**Best solution**: **bunenv** (per-service environments)

.. code-block:: bash

   services/
   ├── api/.venv (Bun 1.3.3)
   ├── worker/.venv (Bun 1.2.0)
   └── frontend/.venv (Bun latest)

   # Each service isolated
   cd services/api && source .venv/bin/activate

Scenario 3: Library Maintainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Needs**: Test against multiple Bun versions

**Best solution**: **bunenv** (test matrix)

.. code-block:: bash

   for version in 1.0.0 1.1.0 1.2.0 1.3.0; do
     bunenv "test-$version" --bun="$version"
     source "test-$version/bin/activate"
     bun test
     deactivate_bun
   done

Scenario 4: Enterprise Developer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Needs**: Controlled environments, corporate proxy

**Best solution**: **bunenv** (with mirror)

.. code-block:: bash

   # Corporate mirror
   bunenv .venv --mirror=https://artifacts.corp.com/bun/releases \
                --github-token=corporate_token

Conclusion
----------

bunenv excels at:

✓ **Project-level isolation**: Each project gets its own Bun

✓ **Python integration**: Works seamlessly with Python tools

✓ **Version pinning**: Reproducible builds across teams

✓ **Simplicity**: Zero configuration, fast setup

It's inspired by nodeenv's proven approach, bringing the same reliability to the Bun ecosystem.

Choose the tool that matches your workflow - and remember, you can often combine tools for the best of both worlds!

Next Steps
----------

- :doc:`migrating` - Migrate from other tools to bunenv
- :doc:`workflows` - See bunenv in action
- :doc:`quickstart` - Try bunenv yourself
