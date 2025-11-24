Configuration Guide
===================

bunenv works great with zero configuration, but offers plenty of customization when you need it.
This guide covers all configuration options and how to use them effectively.

Configuration Methods
---------------------

bunenv supports three configuration methods, in order of precedence:

1. **Command-line arguments** (highest priority)
2. **Configuration files** (``.bunenvrc``, ``setup.cfg``, ``tox.ini``)
3. **Version files** (``.bun-version``)

Command-Line Arguments
----------------------

All options can be passed directly to bunenv:

.. code-block:: bash

   bunenv .venv --bun=1.3.3 --variant=baseline --github-token=ghp_xxx

See :doc:`../api/cli` for a complete list of options.

Configuration Files
-------------------

~/.bunenvrc (User-Level Defaults)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``~/.bunenvrc`` for personal defaults that apply to all bunenv environments:

.. code-block:: ini

   [bunenv]
   bun = latest
   variant =
   github_token = ghp_your_token_here
   prebuilt = True
   ignore_ssl_certs = False
   mirror =

**Location**: ``~/.bunenvrc`` (home directory)

**When to use**: Personal preferences that apply everywhere

**Example use case**: GitHub token to avoid rate limits

Project-Level Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Place configuration in your project's ``setup.cfg`` or ``tox.ini``:

.. code-block:: ini

   # setup.cfg or tox.ini
   [bunenv]
   bun = 1.3.3
   variant = baseline

**Location**: Project root directory

**When to use**: Project-specific Bun version and settings

**Example use case**: Pin Bun version for all team members

Custom Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify a custom config file:

.. code-block:: bash

   bunenv .venv --config-file=./my-config.ini

**When to use**: Multiple configurations for different scenarios

Disable Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use built-in defaults only:

.. code-block:: bash

   bunenv .venv --config-file=

**When to use**: CI/CD where you want explicit control

Configuration Precedence
~~~~~~~~~~~~~~~~~~~~~~~~~

If the same option appears in multiple places:

.. code-block:: text

   Command line
        ↓
   --config-file (if specified)
        ↓
   ./tox.ini
        ↓
   ./setup.cfg
        ↓
   ~/.bunenvrc
        ↓
   Built-in defaults

Later sources override earlier ones.

Version Files
-------------

.bun-version
~~~~~~~~~~~~

Specify the Bun version in a file:

.. code-block:: bash

   echo "1.3.3" > .bun-version
   bunenv .venv  # Uses 1.3.3 automatically

**Format**: Single line with version number

**Prefixes supported**:
- ``1.3.3`` (recommended)
- ``v1.3.3``
- ``bun-v1.3.3``

All are parsed to ``1.3.3``.

**Commit this file**: Yes! This tells teammates which Bun version to use.

.. code-block:: bash

   git add .bun-version
   git commit -m "Pin Bun version to 1.3.3"

Configuration Options Reference
-------------------------------

Bun Version Options
~~~~~~~~~~~~~~~~~~~

``bun``
^^^^^^^

Bun version to install.

**Type**: String

**Default**: ``latest``

**Values**:
- ``latest`` - Most recent stable release
- ``1.3.3`` - Specific version
- ``system`` - Use system Bun (symlink)

**Examples**:

.. code-block:: bash

   bunenv .venv --bun=latest      # Latest stable
   bunenv .venv --bun=1.3.3       # Pin to 1.3.3
   bunenv .venv --bun=system      # Use system Bun

.. code-block:: ini

   [bunenv]
   bun = 1.3.3

.. warning::
   ``system`` mode requires Bun to be installed on your system.
   Not supported on Windows.

``variant``
^^^^^^^^^^^

Bun binary variant to download.

**Type**: String (choice)

**Default**: ``""`` (auto-detect)

**Values**:
- ``""`` - Auto-detect (recommended)
- ``baseline`` - Older CPU support (Nehalem/Bulldozer+)
- ``profile`` - Debug/profiling build
- ``musl`` - Alpine Linux, Void Linux (auto-detected)

**Auto-detection logic**:
- Linux with musl libc → ``musl``
- All others → standard (modern CPU optimizations)

**Examples**:

.. code-block:: bash

   # Auto-detect (recommended)
   bunenv .venv --bun=latest

   # Force baseline for old CPUs
   bunenv .venv --bun=latest --variant=baseline

   # Profiling build
   bunenv .venv --bun=latest --variant=profile

.. code-block:: ini

   [bunenv]
   variant = baseline

**When to use**:
- ``baseline``: Old CPUs without AVX2 (pre-2013)
- ``profile``: Performance debugging
- ``musl``: Usually auto-detected, but force if needed

Network Options
~~~~~~~~~~~~~~~

``github_token``
^^^^^^^^^^^^^^^^

GitHub personal access token for API requests.

**Type**: String

**Default**: ``None``

**Why needed**: GitHub API rate limits:
- Unauthenticated: 60 requests/hour
- Authenticated: 5000 requests/hour

**How to create**:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. No scopes needed for public repos
4. Copy the token (starts with ``ghp_``)

**Examples**:

.. code-block:: bash

   # Command line
   bunenv .venv --github-token=ghp_your_token_here

   # Environment variable
   export GITHUB_TOKEN=ghp_your_token_here
   bunenv .venv --github-token=$GITHUB_TOKEN

.. code-block:: ini

   # ~/.bunenvrc (keep this file private!)
   [bunenv]
   github_token = ghp_your_token_here

.. important::
   **Security**: Keep your token private!

   - Don't commit ``.bunenvrc`` with tokens
   - Use environment variables in CI/CD
   - Tokens in config files should be personal configs only

``mirror``
^^^^^^^^^^

Alternative URL for Bun downloads.

**Type**: String (URL)

**Default**: ``None`` (uses GitHub Releases)

**Format**: Base URL without trailing slash

**Examples**:

.. code-block:: bash

   # Use GitHub mirror
   bunenv .venv --mirror=https://mirror.example.com/bun/releases

.. code-block:: ini

   [bunenv]
   mirror = https://mirror.example.com/bun/releases

**When to use**:
- Corporate proxies
- Geographic mirrors for faster downloads
- Offline installations with local mirror

``ignore_ssl_certs``
^^^^^^^^^^^^^^^^^^^^

Disable SSL certificate verification.

**Type**: Boolean

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv .venv --ignore_ssl_certs

.. code-block:: ini

   [bunenv]
   ignore_ssl_certs = True

.. danger::
   **UNSAFE**: Only use when absolutely necessary (corporate proxy, etc.)
   This disables security verification!

Environment Options
~~~~~~~~~~~~~~~~~~~

``python_virtualenv``
^^^^^^^^^^^^^^^^^^^^^

Install Bun into the active Python virtualenv.

**Type**: Boolean (flag)

**Default**: ``False``

**Requires**: Active Python virtualenv

**Examples**:

.. code-block:: bash

   # Create Python venv
   python -m venv .venv
   source .venv/bin/activate

   # Install bunenv in it
   pip install bunenv

   # Add Bun to the same environment
   bunenv --python-virtualenv --bun=latest

   # Now you have both Python and Bun!
   (venv) $ python --version
   (venv) $ bun --version

.. code-block:: ini

   [bunenv]
   # Can't use this in config - only makes sense as CLI flag

``prompt``
^^^^^^^^^^

Custom prompt prefix when environment is activated.

**Type**: String

**Default**: ``(directory-name)``

**Examples**:

.. code-block:: bash

   # Default
   bunenv .venv
   source .venv/bin/activate
   (.venv) $

   # Custom prompt
   bunenv .venv --prompt="[my-project]"
   source .venv/bin/activate
   [my-project] $

.. code-block:: ini

   [bunenv]
   prompt = [my-app]

Installation Options
~~~~~~~~~~~~~~~~~~~~

``requirements``
^^^^^^^^^^^^^^^^

Install packages from a file after creating environment.

**Type**: String (file path)

**Default**: ``""`` (none)

**Format**: One package per line (like npm's package.json list)

**Example file** (``bun-requirements.txt``):

.. code-block:: text

   # bun-requirements.txt
   express
   typescript
   @types/node

   # Comments are supported
   zod
   drizzle-orm

**Usage**:

.. code-block:: bash

   bunenv .venv --requirements=bun-requirements.txt

.. code-block:: ini

   [bunenv]
   requirements = requirements-bun.txt

``clean_src``
^^^^^^^^^^^^^

Remove downloaded source files after installation.

**Type**: Boolean (flag)

**Default**: ``False``

**What it removes**: ``<env>/src/`` directory with downloaded zip files

**Examples**:

.. code-block:: bash

   bunenv .venv --clean-src

.. code-block:: ini

   [bunenv]
   clean_src = True

**When to use**: Save disk space (saves ~50MB per environment)

``force``
^^^^^^^^^

Overwrite existing environment directory.

**Type**: Boolean (flag)

**Default**: ``False``

**Examples**:

.. code-block:: bash

   # First creation
   bunenv .venv --bun=1.3.3

   # Try to recreate - ERROR!
   bunenv .venv --bun=1.3.4
   # Error: Environment already exists

   # Force recreation
   bunenv .venv --bun=1.3.4 --force
   # OK - overwrites existing

.. warning::
   This will delete the existing environment! Any installed packages will be lost.

Logging Options
~~~~~~~~~~~~~~~

``verbose``
^^^^^^^^^^^

Show detailed output during installation.

**Type**: Boolean (flag)

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv .venv --verbose

**Output comparison**:

.. code-block:: text

   # Normal
   * Install prebuilt Bun (1.3.3) ........ done.

   # Verbose
   * Install prebuilt Bun (1.3.3)
   * Downloading from https://github.com/oven-sh/bun/releases/...
   * Extracting archive
   * Copying binary to .venv/bin/bun
   * Setting permissions
   done.

``quiet``
^^^^^^^^^

Suppress non-error output.

**Type**: Boolean (flag)

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv .venv --quiet

**When to use**: Scripting where you only want errors

Configuration Examples
----------------------

Development Machine Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

Personal defaults in ``~/.bunenvrc``:

.. code-block:: ini

   [bunenv]
   # Always use latest unless overridden
   bun = latest

   # GitHub token for unlimited API requests
   github_token = ghp_your_personal_token

   # Baseline for old laptop CPU
   variant = baseline

   # Verbose output for debugging
   # verbose = True  # Uncomment if needed

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

Team project in ``setup.cfg``:

.. code-block:: ini

   # setup.cfg
   [bunenv]
   # Pin Bun version for consistency
   bun = 1.3.3

   # Requirements file for dependencies
   requirements = requirements-bun.txt

Plus ``.bun-version``:

.. code-block:: bash

   echo "1.3.3" > .bun-version

CI/CD Configuration
~~~~~~~~~~~~~~~~~~~

GitHub Actions with token:

.. code-block:: yaml

   - name: Setup Bun environment
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     run: |
       pip install bunenv
       bunenv .venv --bun=1.3.3 --github-token=$GITHUB_TOKEN --clean-src

Enterprise/Proxy Setup
~~~~~~~~~~~~~~~~~~~~~~

Corporate network with proxy:

.. code-block:: ini

   # ~/.bunenvrc
   [bunenv]
   # Use internal mirror
   mirror = https://artifacts.company.com/bun/releases

   # Self-signed certs (only if absolutely necessary!)
   # ignore_ssl_certs = True

Multi-Project Developer
~~~~~~~~~~~~~~~~~~~~~~~

Keep it simple - let projects control version:

.. code-block:: ini

   # ~/.bunenvrc - minimal global config
   [bunenv]
   github_token = ghp_your_token

Each project has ``.bun-version``:

.. code-block:: bash

   # project-a/.bun-version
   1.3.3

   # project-b/.bun-version
   1.2.0

Environment Variables
---------------------

Set at Runtime
~~~~~~~~~~~~~~

bunenv sets these when you activate:

.. code-block:: bash

   BUN_VIRTUAL_ENV=/path/to/.venv
   BUN_INSTALL=/path/to/.venv
   BUN_INSTALL_BIN=/path/to/.venv/bin
   PATH=/path/to/.venv/bin:$PATH

Check them:

.. code-block:: bash

   source .venv/bin/activate
   (venv) $ echo $BUN_VIRTUAL_ENV
   /path/to/.venv

   (venv) $ echo $BUN_INSTALL
   /path/to/.venv

Used by bunenv
~~~~~~~~~~~~~~

You can set these to influence bunenv behavior:

.. code-block:: bash

   # Use custom config path
   export BUNENV_CONFIG_FILE=/path/to/config.ini
   bunenv .venv

   # Provide GitHub token
   export GITHUB_TOKEN=ghp_your_token
   bunenv .venv --github-token=$GITHUB_TOKEN

Configuration Best Practices
-----------------------------

**DO:**

✓ Use ``.bun-version`` for version pinning in projects

✓ Put personal preferences (token, variant) in ``~/.bunenvrc``

✓ Put project settings in ``setup.cfg`` or ``tox.ini``

✓ Commit ``.bun-version`` and ``setup.cfg`` to version control

✓ Use environment variables for secrets in CI/CD

**DON'T:**

✗ Commit ``~/.bunenvrc`` to Git (it's personal!)

✗ Put secrets in project config files

✗ Use ``ignore_ssl_certs`` unless absolutely necessary

✗ Set ``verbose = True`` in config (too noisy)

✗ Override ``.bun-version`` without documenting why

Troubleshooting Configuration
------------------------------

Check What Config is Being Used
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use verbose mode to see config loading:

.. code-block:: bash

   bunenv .venv --verbose

Look for lines like:

.. code-block:: text

   CONFIG .bunenvrc: github_token = ghp_***
   CONFIG setup.cfg: bun = 1.3.3

Config Not Being Read
~~~~~~~~~~~~~~~~~~~~~

Check file format:

.. code-block:: bash

   # Verify it has [bunenv] section
   cat ~/.bunenvrc

Common mistakes:

.. code-block:: ini

   # WRONG - missing [bunenv] section
   bun = latest

   # RIGHT
   [bunenv]
   bun = latest

Version File Ignored
~~~~~~~~~~~~~~~~~~~~

Make sure it's named exactly ``.bun-version`` (with leading dot):

.. code-block:: bash

   ls -la .bun-version  # Should show file

   # Not these:
   # bun-version (missing dot)
   # .bun_version (underscore instead of dash)

Token Not Working
~~~~~~~~~~~~~~~~~

Verify token is valid:

.. code-block:: bash

   # Test token
   curl -H "Authorization: token ghp_your_token" \
     https://api.github.com/rate_limit

Should show high rate limit (5000).

Next Steps
----------

Now that you understand configuration:

- :doc:`advanced` - Use advanced features effectively
- :doc:`workflows` - See configuration in real-world scenarios
- :doc:`troubleshooting` - Fix configuration-related issues
