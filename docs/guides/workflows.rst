Common Workflows
================

This guide shows you how to use bunenv in real-world scenarios. Each workflow is task-oriented
and ready to copy-paste into your projects.

Development Workflows
---------------------

Local Development with Version Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard workflow for a project with bunenv:

.. code-block:: bash

   # Initial setup
   cd my-project
   bunenv .venv --bun=1.3.3
   echo ".venv/" >> .gitignore  # Don't commit the environment
   echo "1.3.3" > .bun-version  # Do commit the version

   # Daily workflow
   source .venv/bin/activate
   bun install
   bun run dev

   # When done
   deactivate_bun

**Key Points:**

- Put the version in ``.bun-version`` for teammates
- Add ``.venv/`` to ``.gitignore``
- Teammates run ``bunenv .venv`` and it reads the version automatically

Multiple Projects with Different Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keep separate projects isolated:

.. code-block:: bash

   # Legacy project
   cd ~/projects/legacy-app
   bunenv .venv --bun=1.0.0
   source .venv/bin/activate
   (legacy-app) $ bun --version  # 1.0.0

   # Deactivate
   deactivate_bun

   # Modern project
   cd ~/projects/new-app
   bunenv .venv --bun=latest
   source .venv/bin/activate
   (new-app) $ bun --version  # 1.3.3

   # Work continues without conflicts!

Testing Against Multiple Bun Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test your library against different Bun releases:

.. code-block:: bash

   # Test matrix
   for version in 1.0.0 1.1.0 1.2.0 1.3.0; do
     echo "Testing with Bun $version"
     bunenv "test-env-$version" --bun="$version"
     source "test-env-$version/bin/activate"
     bun install
     bun test
     deactivate_bun
   done

   # Cleanup
   rm -rf test-env-*

CI/CD Integration
-----------------

GitHub Actions
~~~~~~~~~~~~~~

Basic workflow for GitHub Actions:

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Test

   on: [push, pull_request]

   jobs:
     test:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Install bunenv
           run: pip install bunenv

         - name: Setup Bun environment
           run: |
             bunenv .venv --bun=1.3.3
             source .venv/bin/activate
             echo "$PWD/.venv/bin" >> $GITHUB_PATH

         - name: Install dependencies
           run: bun install

         - name: Run tests
           run: bun test

Matrix Testing Across Bun Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test against multiple Bun versions:

.. code-block:: yaml

   # .github/workflows/test-matrix.yml
   name: Test Matrix

   on: [push, pull_request]

   jobs:
     test:
       runs-on: ${{ matrix.os }}
       strategy:
         matrix:
           os: [ubuntu-latest, macos-latest, windows-latest]
           bun-version: ['1.0.0', '1.1.0', '1.2.0', 'latest']

       steps:
         - uses: actions/checkout@v4

         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Install bunenv
           run: pip install bunenv

         - name: Setup Bun
           run: bunenv .venv --bun=${{ matrix.bun-version }}

         - name: Activate Bun (Unix)
           if: runner.os != 'Windows'
           run: |
             source .venv/bin/activate
             echo "$PWD/.venv/bin" >> $GITHUB_PATH

         - name: Activate Bun (Windows)
           if: runner.os == 'Windows'
           run: |
             .venv\Scripts\activate.bat
             echo "$PWD\.venv\Scripts" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append

         - name: Run tests
           run: bun test

GitLab CI
~~~~~~~~~

.. code-block:: yaml

   # .gitlab-ci.yml
   image: python:3.11

   stages:
     - test

   test:
     stage: test
     before_script:
       - pip install bunenv
       - bunenv .venv --bun=1.3.3
       - source .venv/bin/activate
     script:
       - bun install
       - bun test

Travis CI
~~~~~~~~~

.. code-block:: yaml

   # .travis.yml
   language: python
   python:
     - "3.11"

   before_install:
     - pip install bunenv
     - bunenv .venv --bun=1.3.3
     - source .venv/bin/activate

   install:
     - bun install

   script:
     - bun test

CircleCI
~~~~~~~~

.. code-block:: yaml

   # .circleci/config.yml
   version: 2.1

   jobs:
     test:
       docker:
         - image: cimg/python:3.11
       steps:
         - checkout
         - run:
             name: Install bunenv
             command: pip install bunenv
         - run:
             name: Setup Bun
             command: |
               bunenv .venv --bun=1.3.3
               source .venv/bin/activate
               echo 'export PATH=$PWD/.venv/bin:$PATH' >> $BASH_ENV
         - run:
             name: Install dependencies
             command: bun install
         - run:
             name: Run tests
             command: bun test

   workflows:
     version: 2
     test:
       jobs:
         - test

Python Integration
------------------

Bun Inside Python Virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Bun and Python together in one environment:

.. code-block:: bash

   # Create Python virtualenv
   python -m venv .venv
   source .venv/bin/activate

   # Install bunenv in the virtualenv
   pip install bunenv

   # Install Bun into the same virtualenv
   bunenv --python-virtualenv --bun=latest

   # Now you have both!
   (venv) $ python --version  # Python 3.11.x
   (venv) $ bun --version     # 1.3.3

   # Deactivate deactivates both
   (venv) $ deactivate_bun
   (venv) $ deactivate

Polyglot Project: Python Backend + Bun Frontend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typical full-stack setup:

.. code-block:: bash

   my-app/
   ├── backend/          # Python code
   │   └── requirements.txt
   ├── frontend/         # Bun/TypeScript code
   │   ├── package.json
   │   └── src/
   ├── .python-version   # Python version
   └── .bun-version      # Bun version

Setup script:

.. code-block:: bash

   #!/bin/bash
   # setup.sh

   # Backend setup
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # Frontend setup (install bunenv in Python venv)
   pip install bunenv
   cd ../frontend
   bunenv --python-virtualenv --bun=$(cat ../.bun-version)
   bun install

   echo "Setup complete! Both Python and Bun are ready."

Using pyproject.toml for Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your Python project uses ``pyproject.toml``, you can configure bunenv there:

.. code-block:: toml

   # pyproject.toml
   [tool.bunenv]
   bun = "1.3.3"
   variant = ""
   github_token = ""  # Or use environment variable

Then run:

.. code-block:: bash

   bunenv --python-virtualenv --config-file=pyproject.toml

Package Management
------------------

Requirements File
~~~~~~~~~~~~~~~~~

Install packages from a requirements file:

.. code-block:: text

   # bun-requirements.txt
   express
   typescript
   @types/node
   zod
   drizzle-orm

Install during environment creation:

.. code-block:: bash

   bunenv .venv --bun=latest --requirements=bun-requirements.txt

Or install later:

.. code-block:: bash

   source .venv/bin/activate
   while read pkg; do
     [[ "$pkg" =~ ^#.*$ ]] && continue  # Skip comments
     bun add "$pkg"
   done < bun-requirements.txt

Global vs Local Packages
~~~~~~~~~~~~~~~~~~~~~~~~~

bunenv environments are isolated, so "global" means "global to this environment":

.. code-block:: bash

   source .venv/bin/activate

   # Install globally in this environment
   (venv) $ bun add --global typescript

   # It's available as a command
   (venv) $ tsc --version

   # But only in this environment!
   (venv) $ deactivate_bun
   $ tsc --version  # Error: command not found

Lock Files and Reproducibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commit ``bun.lockb`` for reproducible installs:

.. code-block:: bash

   # First developer
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun install
   git add bun.lockb .bun-version
   git commit -m "Lock dependencies"

   # Second developer
   git pull
   bunenv .venv  # Reads .bun-version automatically
   source .venv/bin/activate
   bun install  # Uses bun.lockb for exact versions

Platform-Specific Workflows
---------------------------

macOS (Apple Silicon)
~~~~~~~~~~~~~~~~~~~~~

bunenv automatically detects and uses aarch64 binaries:

.. code-block:: bash

   # On M1/M2/M3 Mac
   bunenv .venv --bun=latest

   # Verify it's ARM
   source .venv/bin/activate
   (venv) $ file .venv/bin/bun
   # Output: Mach-O 64-bit executable arm64

For Rosetta compatibility (x64):

.. code-block:: bash

   # Force x64 binary (runs under Rosetta)
   arch -x86_64 bunenv .venv --bun=latest

Alpine Linux / musl
~~~~~~~~~~~~~~~~~~~

bunenv auto-detects musl and downloads the correct variant:

.. code-block:: bash

   # On Alpine Linux
   bunenv .venv --bun=latest
   # Automatically downloads bun-linux-x64-musl

   # Verify
   source .venv/bin/activate
   (venv) $ ldd .venv/bin/bun
   # Shows musl, not glibc

Windows with WSL
~~~~~~~~~~~~~~~~

WSL users should use Linux commands:

.. code-block:: bash

   # Inside WSL
   bunenv .venv --bun=latest
   source .venv/bin/activate  # Linux activation

   # NOT Windows activation

Avoid GitHub API Rate Limits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub limits unauthenticated API requests to 60/hour. For CI or heavy use:

.. code-block:: bash

   # Create token at https://github.com/settings/tokens
   # No scopes needed for public repos

   # One-time use
   bunenv .venv --bun=latest --github-token=ghp_your_token

   # Persistent config
   echo "github_token = ghp_your_token" >> ~/.bunenvrc
   bunenv .venv --bun=latest  # Uses token automatically

   # CI environment variable
   export GITHUB_TOKEN=ghp_your_token
   bunenv .venv --bun=latest --github-token=$GITHUB_TOKEN

Migration Scenarios
-------------------

From System Bun to bunenv
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check current version
   bun --version  # 1.2.0

   # Create environment with same version
   bunenv .venv --bun=1.2.0
   source .venv/bin/activate

   # Move global packages (if any)
   # Note: Bun doesn't have traditional global packages like npm

   # Update your workflow
   # Old: bun install
   # New: source .venv/bin/activate && bun install

From nodeenv to bunenv
~~~~~~~~~~~~~~~~~~~~~~~

If you're migrating from Node.js/nodeenv:

.. code-block:: bash

   # Old Node.js project
   nodeenv .nodeenv --node=18.0.0
   source .nodeenv/bin/activate
   npm install

   # New Bun project
   bunenv .venv --bun=latest
   source .venv/bin/activate
   bun install  # Reads package.json from npm

   # Bun is compatible with npm packages!

From Docker Bun to bunenv
~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace Docker for local development:

.. code-block:: bash

   # Old: Docker-based development
   docker run -v $(pwd):/app oven/bun bun install

   # New: Local isolated environment
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun install

   # Still use Docker for production!

Monorepo Workflows
------------------

Multiple Services, Different Bun Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   my-monorepo/
   ├── services/
   │   ├── api/          # Bun 1.3.0
   │   │   ├── .venv/
   │   │   └── .bun-version
   │   ├── worker/       # Bun 1.2.0
   │   │   ├── .venv/
   │   │   └── .bun-version
   │   └── frontend/     # Bun latest
   │       ├── .venv/
   │       └── .bun-version
   └── setup.sh

Setup script:

.. code-block:: bash

   #!/bin/bash
   # setup.sh

   for service in services/*; do
     echo "Setting up $service..."
     cd "$service"
     bunenv .venv --bun=$(cat .bun-version)
     source .venv/bin/activate
     bun install
     deactivate_bun
     cd ../..
   done

Shared Root Environment
~~~~~~~~~~~~~~~~~~~~~~~

Share one environment across a monorepo:

.. code-block:: bash

   # Root of monorepo
   bunenv .venv --bun=1.3.3

   # All services use the same environment
   echo 'source $(git rev-parse --show-toplevel)/.venv/bin/activate' >> ~/.bashrc

   # Now activate automatically when entering the repo

Automation Scripts
------------------

Auto-Activate on Directory Change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add to your ``.bashrc`` or ``.zshrc``:

.. code-block:: bash

   # Auto-activate bunenv when .venv/ exists
   bunenv_auto_activate() {
     if [[ -f ".venv/bin/activate" ]] && [[ "$VIRTUAL_ENV" != "$PWD/.venv" ]]; then
       source .venv/bin/activate
     fi
   }

   # Hook into directory change
   cd() {
     builtin cd "$@"
     bunenv_auto_activate
   }

Project Initialization Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # init-bun-project.sh

   set -e

   PROJECT_NAME=${1:-my-project}
   BUN_VERSION=${2:-latest}

   echo "Creating Bun project: $PROJECT_NAME"

   # Create directory
   mkdir -p "$PROJECT_NAME"
   cd "$PROJECT_NAME"

   # Create bunenv
   bunenv .venv --bun="$BUN_VERSION"
   source .venv/bin/activate

   # Initialize Bun project
   bun init -y

   # Setup git
   git init
   echo ".venv/" >> .gitignore
   echo "node_modules/" >> .gitignore
   echo "$BUN_VERSION" > .bun-version

   echo "Project ready! Run: cd $PROJECT_NAME && source .venv/bin/activate"

Cleanup Script
~~~~~~~~~~~~~~

Remove unused environments:

.. code-block:: bash

   #!/bin/bash
   # cleanup-bunenvs.sh

   find ~ -type d -name ".venv" -path "*/bin/bun" | while read env; do
     echo "Found: $env"
     read -p "Delete? [y/N] " -n 1 -r
     echo
     if [[ $REPLY =~ ^[Yy]$ ]]; then
       rm -rf "$(dirname "$env")"
       echo "Deleted!"
     fi
   done

Best Practices Summary
----------------------

**DO:**

✓ Use ``.bun-version`` for version pinning

✓ Add ``.venv/`` to ``.gitignore``

✓ Commit ``bun.lockb`` for reproducibility

✓ Use GitHub tokens for CI to avoid rate limits

✓ Create separate environments per project

**DON'T:**

✗ Commit the ``.venv/`` directory

✗ Use ``sudo`` with bunenv

✗ Mix system Bun with environment Bun

✗ Forget to activate before installing packages

✗ Share environments between projects

Next Steps
----------

These workflows should cover most use cases. For more advanced topics:

- :doc:`advanced` - Custom variants, mirrors, edge cases
- :doc:`configuration` - Deep dive into config files and options
- :doc:`troubleshooting` - When things don't work as expected

Got a workflow we missed? `Open an issue <https://github.com/JacobCoffee/bunenv/issues>`_ and we'll add it!
