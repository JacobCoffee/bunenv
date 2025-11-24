Migrating to bunenv
===================

Moving to bunenv from other Bun installation methods is straightforward. This guide covers
common migration scenarios with step-by-step instructions.

From System Bun Installation
-----------------------------

If you installed Bun system-wide (Homebrew, apt, official installer), here's how to migrate.

Current Setup
~~~~~~~~~~~~~

You probably have:

.. code-block:: bash

   # System Bun
   which bun
   # /usr/local/bin/bun or ~/.bun/bin/bun

   bun --version
   # 1.3.3 (same for all projects)

Migration Steps
~~~~~~~~~~~~~~~

**Step 1: Install bunenv**

.. code-block:: bash

   pip install bunenv

**Step 2: Create project environment**

.. code-block:: bash

   cd your-project

   # Check your current Bun version
   bun --version  # e.g., 1.3.3

   # Create environment with same version
   bunenv .venv --bun=1.3.3

   # Pin the version
   echo "1.3.3" > .bun-version

   # Ignore environment directory
   echo ".venv/" >> .gitignore

**Step 3: Update project documentation**

Add to your README:

.. code-block:: markdown

   ## Setup

   ```bash
   # Install bunenv
   pip install bunenv

   # Create Bun environment
   bunenv .venv

   # Activate
   source .venv/bin/activate

   # Install dependencies
   bun install
   ```

**Step 4: Update scripts/Makefile**

.. code-block:: makefile

   # Before
   run:
       bun run dev

   # After
   run:
       source .venv/bin/activate && bun run dev

**Step 5: Test the migration**

.. code-block:: bash

   # Activate environment
   source .venv/bin/activate

   # Verify version
   (venv) $ bun --version
   1.3.3

   # Test your app
   (venv) $ bun install
   (venv) $ bun test
   (venv) $ bun run dev

**Step 6: (Optional) Remove system Bun**

Once confident everything works:

.. code-block:: bash

   # Homebrew
   brew uninstall bun

   # Official installer
   rm -rf ~/.bun

   # apt/dnf
   sudo apt remove bun

.. tip::
   Keep system Bun during transition to have a fallback!

From nodeenv
------------

If you use nodeenv for Node.js, migrating to bunenv for Bun is natural.

Side-by-Side Comparison
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - nodeenv (Node.js)
     - bunenv (Bun)
   * - ``nodeenv .nodeenv``
     - ``bunenv .venv``
   * - ``source .nodeenv/bin/activate``
     - ``source .venv/bin/activate``
   * - ``deactivate_node``
     - ``deactivate_bun``
   * - ``.node-version``
     - ``.bun-version``
   * - ``--node=18.0.0``
     - ``--bun=1.3.3``

Migration Example
~~~~~~~~~~~~~~~~~

**Existing Node.js project**:

.. code-block:: bash

   # Old setup
   nodeenv .nodeenv --node=18.0.0
   source .nodeenv/bin/activate
   npm install

**Migrating to Bun**:

.. code-block:: bash

   # Create Bun environment
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate

   # Bun can read package.json from npm!
   bun install  # Reads existing package.json

   # Test your app
   bun run dev

**Keeping both** (if you still need Node.js):

.. code-block:: bash

   # Both environments coexist
   nodeenv .nodeenv --node=18.0.0
   bunenv .venv --bun=1.3.3

   # Use Node.js
   source .nodeenv/bin/activate
   npm run build
   deactivate_node

   # Switch to Bun
   source .venv/bin/activate
   bun run dev
   deactivate_bun

Key Differences
~~~~~~~~~~~~~~~

**Package installation**:

.. code-block:: bash

   # nodeenv + npm
   npm install express
   npm install --save-dev typescript

   # bunenv + bun
   bun add express
   bun add -d typescript

**Running scripts**:

.. code-block:: bash

   # nodeenv + npm
   npm run dev
   npm test

   # bunenv + bun
   bun run dev
   bun test

**Global packages**:

.. code-block:: bash

   # nodeenv + npm
   npm install -g typescript

   # bunenv + bun
   bun add -g typescript  # Global to environment

From Docker-Based Development
------------------------------

If you use Docker for Bun development, bunenv can speed up local iteration.

Current Docker Setup
~~~~~~~~~~~~~~~~~~~~

Typical Dockerfile:

.. code-block:: dockerfile

   FROM oven/bun:1.3.3

   WORKDIR /app
   COPY package.json bun.lockb ./
   RUN bun install

   COPY . .
   CMD ["bun", "run", "start"]

Development workflow:

.. code-block:: bash

   # Build image
   docker build -t myapp .

   # Run with volume mount
   docker run -v $(pwd):/app -p 3000:3000 myapp

Migration to Hybrid Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Keep Docker for production**, use bunenv for development:

.. code-block:: bash

   # Development (bunenv)
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun install
   bun run dev  # Fast local iteration!

   # Production (Docker)
   docker build -t myapp .
   docker run myapp

**Update your development documentation**:

.. code-block:: markdown

   ## Development

   ```bash
   # Setup
   bunenv .venv
   source .venv/bin/activate
   bun install

   # Run locally
   bun run dev
   ```

   ## Production

   ```bash
   docker build -t myapp .
   docker run -p 3000:3000 myapp
   ```

Benefits of This Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~

✓ **Faster local development**: No container overhead

✓ **Native IDE integration**: Better debugging, autocomplete

✓ **Production parity**: Still use Docker for deployment

✓ **Resource efficiency**: Lower CPU/memory usage

When to Keep Docker for Dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Continue using Docker if you:

- Need Linux environment on macOS/Windows
- Require additional services (database, Redis, etc.)
- Want exact production environment
- Develop on multiple platforms

From asdf/mise
--------------

Migrating from asdf or mise to bunenv provides stronger isolation.

asdf Setup
~~~~~~~~~~

Current workflow:

.. code-block:: bash

   # Install Bun plugin
   asdf plugin add bun

   # Install version
   asdf install bun 1.3.3

   # Set version
   cd project
   echo "bun 1.3.3" > .tool-versions
   asdf local bun 1.3.3

Migration Steps
~~~~~~~~~~~~~~~

**Step 1: Note your Bun version**

.. code-block:: bash

   cd your-project
   cat .tool-versions
   # bun 1.3.3

**Step 2: Create bunenv environment**

.. code-block:: bash

   # Install bunenv
   pip install bunenv

   # Create environment
   bunenv .venv --bun=1.3.3

   # Pin version
   echo "1.3.3" > .bun-version

**Step 3: Update activation**

.. code-block:: bash

   # Old: asdf auto-switches
   cd project  # asdf switches to Bun 1.3.3 automatically

   # New: explicit activation
   cd project
   source .venv/bin/activate

**Step 4: (Optional) Auto-activation**

Add to `.bashrc` or `.zshrc`:

.. code-block:: bash

   # Auto-activate bunenv on cd
   bunenv_auto() {
     if [[ -f ".venv/bin/activate" ]]; then
       source .venv/bin/activate
     fi
   }

   # Hook into cd
   cd() {
     builtin cd "$@"
     bunenv_auto
   }

Comparison Table
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Feature
     - asdf/mise
     - bunenv
   * - **Activation**
     - Automatic (shell hook)
     - Manual or scripted
   * - **Isolation**
     - Version switching
     - Full environment
   * - **Multiple active**
     - One per shell
     - Unlimited
   * - **Config file**
     - .tool-versions
     - .bun-version
   * - **Python integration**
     - Separate
     - Native

Why Migrate?
~~~~~~~~~~~~

Consider bunenv if you:

✓ Need true isolation, not just version switching

✓ Want multiple Bun versions active simultaneously

✓ Prefer Python-based tooling

✓ Don't want shell-level hooks

Team Migration
--------------

Migrating an entire team requires coordination.

Planning the Migration
~~~~~~~~~~~~~~~~~~~~~~

**Week 1: Pilot**

.. code-block:: bash

   # One developer tests bunenv
   pip install bunenv
   bunenv .venv --bun=1.3.3
   source .venv/bin/activate
   bun install
   bun test

   # Document any issues

**Week 2: Documentation**

Create team guide:

.. code-block:: markdown

   # Bun Environment Setup

   ## Prerequisites
   - Python 3.10+
   - pip or uv

   ## Installation
   ```bash
   pip install bunenv
   ```

   ## Usage
   ```bash
   # First time setup
   bunenv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate.bat  # Windows

   # Daily workflow
   source .venv/bin/activate
   bun install
   bun run dev
   ```

**Week 3: Migration**

.. code-block:: bash

   # Update repository
   echo "1.3.3" > .bun-version
   echo ".venv/" >> .gitignore

   # Update README
   # Update CI/CD (if needed)

   # Commit
   git add .bun-version .gitignore README.md
   git commit -m "feat: migrate to bunenv for Bun management"

**Week 4: Support**

- Help team members with setup
- Answer questions
- Fix edge cases

Migration Checklist
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   [ ] Install bunenv in dev environment
   [ ] Create .venv with project's Bun version
   [ ] Add .bun-version to repository
   [ ] Update .gitignore
   [ ] Update README with setup instructions
   [ ] Update Makefile/scripts
   [ ] Update CI/CD pipelines
   [ ] Test all workflows
   [ ] Document in team wiki
   [ ] Train team members
   [ ] Remove old installation method

CI/CD Migration
---------------

Migrating CI/CD to bunenv ensures reproducible builds.

GitHub Actions
~~~~~~~~~~~~~~

**Before** (system install):

.. code-block:: yaml

   - name: Setup Bun
     uses: oven-sh/setup-bun@v1
     with:
       bun-version: 1.3.3

**After** (bunenv):

.. code-block:: yaml

   - name: Setup Python
     uses: actions/setup-python@v5
     with:
       python-version: '3.11'

   - name: Install bunenv
     run: pip install bunenv

   - name: Setup Bun environment
     run: |
       bunenv .venv --bun=1.3.3
       source .venv/bin/activate
       echo "$PWD/.venv/bin" >> $GITHUB_PATH

GitLab CI
~~~~~~~~~

**Before**:

.. code-block:: yaml

   before_script:
     - curl -fsSL https://bun.sh/install | bash
     - export PATH="$HOME/.bun/bin:$PATH"

**After**:

.. code-block:: yaml

   before_script:
     - pip install bunenv
     - bunenv .venv
     - source .venv/bin/activate

Travis CI
~~~~~~~~~

**Before**:

.. code-block:: yaml

   before_install:
     - curl -fsSL https://bun.sh/install | bash
     - source ~/.bashrc

**After**:

.. code-block:: yaml

   before_install:
     - pip install bunenv
     - bunenv .venv
     - source .venv/bin/activate

Benefits in CI/CD
~~~~~~~~~~~~~~~~~

✓ **Version pinning**: `.bun-version` ensures consistency

✓ **Caching**: Cache `.venv` directory

✓ **Python integration**: If you use Python tools

✓ **No shell hacks**: Clean, declarative setup

Rollback Strategy
-----------------

If migration doesn't work out, rolling back is easy.

Quick Rollback
~~~~~~~~~~~~~~

.. code-block:: bash

   # Deactivate bunenv
   deactivate_bun

   # Reinstall system Bun
   curl -fsSL https://bun.sh/install | bash

   # Remove bunenv
   rm -rf .venv
   pip uninstall bunenv

   # Restore old workflow
   source ~/.bashrc
   bun install

Keeping Both
~~~~~~~~~~~~

No need to choose - keep both during transition:

.. code-block:: bash

   # bunenv for new projects
   cd new-project
   bunenv .venv --bun=latest
   source .venv/bin/activate

   # System Bun for old projects
   cd old-project
   bun install  # Uses system Bun

Common Migration Issues
-----------------------

PATH Conflicts
~~~~~~~~~~~~~~

**Symptom**: Wrong Bun version running

**Solution**:

.. code-block:: bash

   # Check which Bun is active
   which bun
   # Should show .venv/bin/bun when activated

   # If not, check PATH
   echo $PATH | tr ':' '\n' | head -5

   # Reactivate
   deactivate_bun
   source .venv/bin/activate

Package Lock Files
~~~~~~~~~~~~~~~~~~

**Symptom**: `bun.lockb` changes unexpectedly

**Solution**:

.. code-block:: bash

   # Remove lock file
   rm bun.lockb

   # Regenerate with bunenv's Bun
   source .venv/bin/activate
   bun install

Team Synchronization
~~~~~~~~~~~~~~~~~~~~

**Symptom**: Different team members use different versions

**Solution**:

.. code-block:: bash

   # Enforce version in repository
   echo "1.3.3" > .bun-version
   git add .bun-version
   git commit -m "Pin Bun version to 1.3.3"

   # Team members run:
   bunenv .venv  # Reads .bun-version automatically

Success Stories
---------------

Example: Byte Bot Project
~~~~~~~~~~~~~~~~~~~~~~~~~

The `Byte Bot <https://github.com/JacobCoffee/byte>`_ project migrated from system Bun to bunenv:

**Before**:

.. code-block:: bash

   # Developers had different Bun versions
   # Frontend builds varied
   # CI sometimes failed

**After**:

.. code-block:: bash

   # Everyone uses same version via .bun-version
   bunenv .venv
   source .venv/bin/activate
   bun install

**Results**:

- Consistent builds across team
- Faster onboarding (one command setup)
- CI reliability improved

Getting Help During Migration
------------------------------

If you encounter issues:

1. **Check troubleshooting guide**: :doc:`troubleshooting`
2. **Review comparison**: :doc:`comparison`
3. **Ask for help**: https://github.com/JacobCoffee/bunenv/discussions
4. **Open an issue**: https://github.com/JacobCoffee/bunenv/issues

Next Steps
----------

After migration:

- :doc:`workflows` - Learn bunenv best practices
- :doc:`configuration` - Optimize your setup
- :doc:`advanced` - Explore advanced features

Welcome to bunenv! You're now set up for isolated, reproducible Bun environments.
