Quick Start Tutorial
====================

Welcome! In the next 5 minutes, you'll create your first isolated Bun environment and understand
how bunenv keeps your projects organized.

What You'll Learn
-----------------

By the end of this tutorial, you'll know how to:

1. Install bunenv
2. Create a Bun environment
3. Activate and use the environment
4. Install packages in isolation
5. Deactivate when you're done

Prerequisites
-------------

Just two things:

- **Python 3.10+** (check with ``python --version``)

No Bun installation needed - bunenv handles that for you!

Step 1: Install bunenv
----------------------

Choose your preferred method:

Using pip
~~~~~~~~~

.. code-block:: bash

   pip install bunenv

Using uv (Faster)
~~~~~~~~~~~~~~~~~

If you have `uv <https://github.com/astral-sh/uv>`_ installed:

.. code-block:: bash

   uv tool install bunenv

Using pipx (Isolated)
~~~~~~~~~~~~~~~~~~~~~

For a completely isolated bunenv installation:

.. code-block:: bash

   pipx install bunenv

Verify Installation
~~~~~~~~~~~~~~~~~~~

Check that bunenv is installed:

.. code-block:: bash

   bunenv --version

You should see something like ``0.1.0``.

.. tip::
   If you get "command not found", make sure your Python scripts directory is in your PATH.
   Try ``python -m bunenv --version`` as an alternative.

Step 2: Create Your First Environment
--------------------------------------

Let's create a Bun environment for a new project:

.. code-block:: bash

   bunenv my-first-env

You'll see output like this:

.. code-block:: text

   * Install prebuilt Bun (1.3.3) ........ done.
   * Creating: my-first-env/bin ... done.

What Just Happened?
~~~~~~~~~~~~~~~~~~~

bunenv just:

1. Fetched the latest Bun version from GitHub Releases
2. Downloaded the appropriate binary for your platform
3. Created a directory structure at ``my-first-env/``
4. Installed activation scripts

Let's peek at what was created:

.. code-block:: bash

   ls -la my-first-env/

You'll see:

.. code-block:: text

   my-first-env/
   ├── bin/                  # Bun binary and activation scripts
   │   ├── bun              # The Bun executable
   │   ├── activate         # Bash/zsh activation
   │   ├── activate.fish    # Fish shell activation
   │   └── shim            # System bun compatibility
   └── src/                 # Downloaded files (optional cleanup)

Step 3: Activate the Environment
---------------------------------

Time to activate! The command varies by platform:

macOS / Linux (bash/zsh)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   source my-first-env/bin/activate

macOS / Linux (fish)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   source my-first-env/bin/activate.fish

Windows (PowerShell)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   my-first-env\Scripts\Activate.ps1

Windows (cmd.exe)
~~~~~~~~~~~~~~~~~

.. code-block:: bat

   my-first-env\Scripts\activate.bat

What Changed?
~~~~~~~~~~~~~

After activation, notice:

1. **Your prompt changed**: You'll see ``(my-first-env)`` at the start
2. **``bun`` is now available**: It's the isolated version, not system Bun
3. **Environment variables are set**: ``BUN_VIRTUAL_ENV``, ``BUN_INSTALL``, etc.

Verify it worked:

.. code-block:: bash

   (my-first-env) $ bun --version
   1.3.3

   (my-first-env) $ which bun  # macOS/Linux
   /path/to/my-first-env/bin/bun

.. note::
   The ``(my-first-env)`` prefix shows you're in an activated environment.
   This is your visual reminder that you're working in isolation!

Step 4: Use Bun
---------------

Now let's actually use Bun to build something. We'll create a simple project:

Initialize a Project
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   (my-first-env) $ bun init

Bun will ask you some questions. Just press Enter to accept defaults:

.. code-block:: text

   bun init helps you get started with a minimal project and tries to
   guess sensible defaults. Press ^C anytime to quit

   package name (my-first-env):
   entry point (index.ts):

   Done! A package.json file was saved in the current directory.

Install a Package
~~~~~~~~~~~~~~~~~

Let's install Express, a popular web framework:

.. code-block:: bash

   (my-first-env) $ bun add express

You'll see:

.. code-block:: text

   bun add v1.3.3
   [0.51ms] installed express@4.18.2

The package is installed in ``node_modules/`` within your project - not globally!

Create a Simple Server
~~~~~~~~~~~~~~~~~~~~~~

Create a file called ``server.js``:

.. code-block:: javascript

   // server.js
   import express from 'express';

   const app = express();
   const port = 3000;

   app.get('/', (req, res) => {
     res.send('Hello from my isolated Bun environment!');
   });

   app.listen(port, () => {
     console.log(`Server running at http://localhost:${port}`);
   });

Run Your Server
~~~~~~~~~~~~~~~

.. code-block:: bash

   (my-first-env) $ bun run server.js

Open http://localhost:3000 in your browser. You'll see:

.. code-block:: text

   Hello from my isolated Bun environment!

Congratulations! You just ran a web server using your isolated Bun installation.

Press Ctrl+C to stop the server.

Step 5: Deactivate
------------------

When you're done working, deactivate the environment:

.. code-block:: bash

   (my-first-env) $ deactivate_bun

Notice:

1. The ``(my-first-env)`` prompt prefix disappears
2. ``bun`` command now points back to your system Bun (if installed)
3. Environment variables are restored

Test it:

.. code-block:: bash

   $ bun --version  # Will error if you don't have system Bun

The isolated Bun is gone from your PATH. Your system is back to normal!

.. important::
   Deactivating doesn't delete the environment - it just stops using it.
   You can re-activate anytime with ``source my-first-env/bin/activate``.

What You've Learned
-------------------

In just 5 minutes, you:

✓ Installed bunenv

✓ Created an isolated Bun environment

✓ Activated and used it

✓ Installed packages that only exist in that environment

✓ Ran a real application

✓ Deactivated to return to normal

Try It Yourself: Different Versions
------------------------------------

Here's where it gets powerful. Create a second environment with a different Bun version:

.. code-block:: bash

   # Create environment with Bun 1.0.0
   bunenv old-project --bun=1.0.0

   # Activate it
   source old-project/bin/activate

   # Check version
   (old-project) $ bun --version
   1.0.0

   # Deactivate
   (old-project) $ deactivate_bun

   # Now activate the first environment
   source my-first-env/bin/activate

   # Check version
   (my-first-env) $ bun --version
   1.3.3

See? Different projects, different Bun versions, zero conflicts.

Real-World Workflow Example
---------------------------

Here's how you'd use bunenv in a typical project:

.. code-block:: bash

   # Clone a project
   git clone https://github.com/username/my-bun-app.git
   cd my-bun-app

   # Create Bun environment (specific version)
   bunenv .venv --bun=1.3.3

   # Activate
   source .venv/bin/activate

   # Install project dependencies
   bun install

   # Run development server
   bun run dev

   # When done for the day
   deactivate_bun

Next time you work on the project:

.. code-block:: bash

   cd my-bun-app
   source .venv/bin/activate  # Back in business!
   bun run dev

Common Questions
----------------

**Q: Do I need to install Bun separately?**

No! bunenv downloads and installs Bun for you.

**Q: Can I have multiple environments?**

Absolutely! Create as many as you want, each with different Bun versions.

**Q: What if I want the latest Bun?**

That's the default! Just use ``bunenv myenv`` without specifying ``--bun``.

**Q: How do I delete an environment?**

Just delete the directory: ``rm -rf my-first-env``

**Q: Can I use this in CI/CD?**

Yes! bunenv is perfect for reproducible builds. See :doc:`workflows` for examples.

**Q: Does this work on Windows?**

Yes! bunenv supports Windows with PowerShell and cmd.exe.

Next Steps
----------

Now that you've got the basics, explore:

.. grid:: 2

   .. grid-item-card:: Common Workflows
      :link: workflows
      :link-type: doc

      Learn patterns for CI/CD, Python integration, and more.

   .. grid-item-card:: Configuration
      :link: configuration
      :link-type: doc

      Set defaults, use GitHub tokens, and customize behavior.

   .. grid-item-card:: Advanced Features
      :link: advanced
      :link-type: doc

      CPU variants, mirrors, requirements files, and more.

   .. grid-item-card:: Troubleshooting
      :link: troubleshooting
      :link-type: doc

      Solutions to common problems and error messages.

You're now ready to use bunenv in your projects. Happy coding!
