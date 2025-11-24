Command-Line Interface
======================

Complete reference for bunenv's command-line options.

Synopsis
--------

.. code-block:: text

   bunenv [OPTIONS] DEST_DIR
   bunenv --list
   bunenv --version

Description
-----------

bunenv creates isolated Bun environments, similar to Python's virtualenv.

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Create environment with latest Bun
   bunenv myenv

   # Create with specific version
   bunenv myenv --bun=1.3.3

   # List available Bun versions
   bunenv --list

   # Show bunenv version
   bunenv --version

Positional Arguments
--------------------

DEST_DIR
~~~~~~~~

Destination directory for the Bun environment.

**Type**: String (path)

**Required**: Yes (unless using ``--list`` or ``--python-virtualenv``)

**Examples**:

.. code-block:: bash

   bunenv myenv              # Relative path
   bunenv /opt/bunenv        # Absolute path
   bunenv .venv              # Common convention
   bunenv ~/projects/env     # Home directory

Version Options
---------------

\--version
~~~~~~~~~~

Show bunenv version and exit.

.. code-block:: bash

   bunenv --version
   # Output: 0.1.0

-b, \--bun BUN_VER
~~~~~~~~~~~~~~~~~~

Specify Bun version to install.

**Type**: String

**Default**: ``latest``

**Values**:

- ``latest`` - Most recent stable release
- ``X.Y.Z`` - Specific version (e.g., ``1.3.3``)
- ``system`` - Use system-installed Bun

**Examples**:

.. code-block:: bash

   bunenv myenv --bun=latest     # Latest stable
   bunenv myenv --bun=1.3.3      # Pin to 1.3.3
   bunenv myenv -b 1.0.0         # Short form

**System Bun**:

.. code-block:: bash

   bunenv myenv --bun=system

.. warning::
   ``--bun=system`` is not supported on Windows.

-l, \--list
~~~~~~~~~~~

List all available Bun versions from GitHub Releases and exit.

.. code-block:: bash

   bunenv --list

**Output** (example):

.. code-block:: text

   1.3.3    1.3.2    1.3.1    1.3.0    1.2.15   1.2.14   1.2.13   1.2.12
   1.2.11   1.2.10   1.2.9    1.2.8    1.2.7    1.2.6    1.2.5    1.2.4
   ...

\--variant VARIANT
~~~~~~~~~~~~~~~~~~

Specify Bun binary variant.

**Type**: Choice

**Default**: ``""`` (auto-detect)

**Choices**: ``""``, ``baseline``, ``profile``, ``musl``

**Auto-detection**:

- Linux with musl → ``musl``
- All others → standard (default)

**Examples**:

.. code-block:: bash

   # Auto-detect (recommended)
   bunenv myenv --bun=1.3.3

   # Force baseline for old CPUs
   bunenv myenv --bun=1.3.3 --variant=baseline

   # musl for Alpine Linux
   bunenv myenv --bun=1.3.3 --variant=musl

   # Profile build for debugging
   bunenv myenv --bun=1.3.3 --variant=profile

**Variant Comparison**:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Variant
     - Use Case
     - CPU Requirement
   * - Standard (default)
     - Modern systems
     - Haswell/Excavator+ (2013+)
   * - Baseline
     - Older systems
     - Nehalem/Bulldozer+ (2008+)
   * - Musl
     - Alpine/Void Linux
     - Any (musl libc)
   * - Profile
     - Development/debugging
     - Any

Network Options
---------------

\--github-token TOKEN
~~~~~~~~~~~~~~~~~~~~~

GitHub personal access token for API requests.

**Type**: String

**Default**: None

**Why needed**: Avoid GitHub API rate limits (60/hour → 5000/hour)

**Examples**:

.. code-block:: bash

   # Direct
   bunenv myenv --github-token=ghp_your_token_here

   # From environment variable
   export GITHUB_TOKEN=ghp_your_token
   bunenv myenv --github-token=$GITHUB_TOKEN

   # From config file
   echo "github_token = ghp_your_token" >> ~/.bunenvrc
   bunenv myenv  # Uses token from config

**Creating a token**:

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. No scopes needed for public repos
4. Copy token (``ghp_...``)

.. seealso::
   :doc:`../guides/configuration` for managing tokens securely

\--mirror URL
~~~~~~~~~~~~~

Set alternative mirror URL for Bun downloads.

**Type**: String (URL)

**Default**: ``https://github.com/oven-sh/bun/releases/download``

**Examples**:

.. code-block:: bash

   # Corporate mirror
   bunenv myenv --mirror=https://artifacts.corp.com/bun/releases

   # Local mirror
   bunenv myenv --mirror=http://localhost:8000

**Mirror URL format**:

.. code-block:: text

   {mirror}/bun-v{version}/bun-{platform}-{arch}[-{variant}].zip

\--ignore_ssl_certs
~~~~~~~~~~~~~~~~~~~

Disable SSL certificate verification.

**Type**: Boolean flag

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv myenv --ignore_ssl_certs

.. danger::
   **UNSAFE**: Only use when absolutely necessary (corporate proxy with self-signed certs).
   This disables security verification!

Installation Options
--------------------

-r, \--requirements FILENAME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install packages from requirements file after creating environment.

**Type**: String (file path)

**Default**: None

**File format**: One package per line

**Example file** (``requirements-bun.txt``):

.. code-block:: text

   express
   typescript
   @types/node
   zod

**Usage**:

.. code-block:: bash

   bunenv myenv --requirements=requirements-bun.txt

**Equivalent to**:

.. code-block:: bash

   bunenv myenv
   source myenv/bin/activate
   bun add express typescript @types/node zod

-c, \--clean-src
~~~~~~~~~~~~~~~~

Remove downloaded source files after installation.

**Type**: Boolean flag

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv myenv --clean-src

**Effect**: Removes ``myenv/src/`` directory (~50MB saved)

**When to use**: Save disk space (recommended for production environments)

\--force
~~~~~~~~

Overwrite existing environment directory.

**Type**: Boolean flag

**Default**: ``False``

**Examples**:

.. code-block:: bash

   # First creation
   bunenv myenv --bun=1.3.3

   # Try again - ERROR
   bunenv myenv --bun=1.3.4
   # Error: Environment already exists

   # Force overwrite
   bunenv myenv --bun=1.3.4 --force

.. warning::
   This deletes the existing environment! Installed packages will be lost.

\--prebuilt
~~~~~~~~~~~

Install Bun from prebuilt binaries.

**Type**: Boolean flag

**Default**: ``True``

**Examples**:

.. code-block:: bash

   bunenv myenv --prebuilt

.. note::
   This is the only option for Bun (no source builds available). Flag exists for nodeenv compatibility.

\--update
~~~~~~~~~

Install packages from requirements file into existing environment without creating new Bun install.

**Type**: Boolean flag

**Default**: ``False``

**Examples**:

.. code-block:: bash

   # Create environment
   bunenv myenv

   # Later, update packages
   bunenv --update --requirements=new-packages.txt

Environment Options
-------------------

-p, \--python-virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~

Install Bun into the current Python virtualenv instead of creating new directory.

**Type**: Boolean flag

**Default**: ``False``

**Requires**: Active Python virtualenv

**Examples**:

.. code-block:: bash

   # Create Python venv
   python -m venv .venv
   source .venv/bin/activate

   # Install bunenv
   pip install bunenv

   # Add Bun to same environment
   bunenv --python-virtualenv --bun=1.3.3

   # Now have both
   (venv) $ python --version  # Python 3.11.x
   (venv) $ bun --version     # 1.3.3

\--prompt PROMPT
~~~~~~~~~~~~~~~~

Custom shell prompt prefix when environment is activated.

**Type**: String

**Default**: ``(directory-name)``

**Examples**:

.. code-block:: bash

   # Default
   bunenv myenv
   source myenv/bin/activate
   (myenv) $

   # Custom
   bunenv myenv --prompt="[my-app] "
   source myenv/bin/activate
   [my-app] $

   # Empty (no prompt change)
   bunenv myenv --prompt=""
   source myenv/bin/activate
   $

Configuration Options
---------------------

-C, \--config-file FILE
~~~~~~~~~~~~~~~~~~~~~~~

Load configuration from custom file.

**Type**: String (file path)

**Default**: ``["./tox.ini", "./setup.cfg", "~/.bunenvrc"]`` (checked in order)

**Examples**:

.. code-block:: bash

   # Use custom config
   bunenv myenv --config-file=./bunenv.ini

   # Disable all config files (use built-in defaults)
   bunenv myenv --config-file=

**Config file format**:

.. code-block:: ini

   [bunenv]
   bun = 1.3.3
   variant = baseline
   github_token = ghp_xxx

Logging Options
---------------

-v, \--verbose
~~~~~~~~~~~~~~

Enable verbose output showing detailed installation steps.

**Type**: Boolean flag

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv myenv --verbose

**Output comparison**:

.. code-block:: text

   # Normal
   * Install prebuilt Bun (1.3.3) ........ done.

   # Verbose
   * Install prebuilt Bun (1.3.3)
    * Creating: myenv/bin ... done.
    * Downloading from https://github.com/oven-sh/bun/...
    * Extracting archive
    * Copying binary
   done.

-q, \--quiet
~~~~~~~~~~~~

Suppress non-error output.

**Type**: Boolean flag

**Default**: ``False``

**Examples**:

.. code-block:: bash

   bunenv myenv --quiet

**When to use**: Scripting, CI/CD where you only want error output

Usage Examples
--------------

Basic Examples
~~~~~~~~~~~~~~

.. code-block:: bash

   # Minimal - latest Bun
   bunenv myenv

   # Specific version
   bunenv myenv --bun=1.3.3

   # Old CPU support
   bunenv myenv --bun=1.3.3 --variant=baseline

   # With requirements
   bunenv myenv --requirements=packages.txt

Advanced Examples
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Full-featured setup
   bunenv myenv \
     --bun=1.3.3 \
     --variant=baseline \
     --requirements=requirements-bun.txt \
     --github-token=$GITHUB_TOKEN \
     --clean-src \
     --prompt="[my-app] "

   # Corporate environment
   bunenv myenv \
     --mirror=https://artifacts.corp.com/bun/releases \
     --github-token=$CORP_GITHUB_TOKEN \
     --ignore_ssl_certs  # Only if necessary!

   # Python integration
   python -m venv .venv
   source .venv/bin/activate
   pip install bunenv
   bunenv --python-virtualenv --bun=1.3.3

CI/CD Examples
~~~~~~~~~~~~~~

**GitHub Actions**:

.. code-block:: yaml

   - name: Setup Bun
     run: |
       pip install bunenv
       bunenv .venv --bun=1.3.3 --clean-src --quiet
       source .venv/bin/activate
       echo "$PWD/.venv/bin" >> $GITHUB_PATH

**GitLab CI**:

.. code-block:: yaml

   before_script:
     - pip install bunenv
     - bunenv .venv --bun=1.3.3 --quiet
     - source .venv/bin/activate

Exit Codes
----------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Code
     - Meaning
   * - ``0``
     - Success
   * - ``1``
     - General error (network, file system, etc.)
   * - ``2``
     - Invalid arguments or environment already exists (without ``--force``)

Environment Variables
---------------------

Variables Set by bunenv
~~~~~~~~~~~~~~~~~~~~~~~

When environment is activated:

.. code-block:: bash

   BUN_VIRTUAL_ENV=/path/to/environment
   BUN_INSTALL=/path/to/environment
   BUN_INSTALL_BIN=/path/to/environment/bin
   PATH=/path/to/environment/bin:$PATH

Variables Used by bunenv
~~~~~~~~~~~~~~~~~~~~~~~~~

bunenv reads these if set:

.. code-block:: bash

   # Used for GitHub token
   GITHUB_TOKEN=ghp_xxx

   # Disable prompt changes
   BUN_VIRTUAL_ENV_DISABLE_PROMPT=1

Files and Directories
---------------------

Created by bunenv
~~~~~~~~~~~~~~~~~

.. code-block:: text

   myenv/
   ├── bin/                   # Unix (macOS/Linux)
   │   ├── activate           # Bash/zsh activation
   │   ├── activate.fish      # Fish shell activation
   │   ├── bun               # Bun executable
   │   └── shim              # System bun wrapper
   ├── Scripts/               # Windows
   │   ├── activate.bat       # cmd.exe activation
   │   ├── Activate.ps1       # PowerShell activation
   │   └── bun.exe           # Bun executable
   ├── install/
   │   └── cache/            # Bun package cache
   └── src/                  # Downloaded files (optional)
       └── bun-*/

Configuration Files
~~~~~~~~~~~~~~~~~~~

bunenv reads (in order):

1. ``./tox.ini``
2. ``./setup.cfg``
3. ``~/.bunenvrc``
4. ``.bun-version`` (version only)
5. Custom file via ``--config-file``

See Also
--------

- :doc:`../guides/quickstart` - Getting started tutorial
- :doc:`../guides/configuration` - Configuration guide
- :doc:`../guides/workflows` - Usage examples
- :doc:`index` - API reference

Reporting Bugs
--------------

Report issues at: https://github.com/JacobCoffee/bunenv/issues

Include:

- bunenv version (``bunenv --version``)
- Full command run
- Error output (with ``--verbose``)
- Platform information

Author
------

Jacob Coffee <jacob@z7x.org>

Adapted from nodeenv by Eugene Kalinin.

License
-------

BSD-3-Clause

See: https://github.com/JacobCoffee/bunenv/blob/main/LICENSE
