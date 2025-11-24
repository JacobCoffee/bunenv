User Guides
===========

Welcome to the bunenv user guides! This section provides comprehensive documentation organized by learning style.

.. note::
   New to bunenv? Start with the :doc:`quickstart` tutorial to get your first environment running in 5 minutes.

Getting Started
---------------

.. toctree::
   :maxdepth: 1

   quickstart

The quickstart tutorial walks you through creating your first Bun environment step-by-step.
Perfect for first-time users who want to see bunenv in action.

How-To Guides
-------------

.. toctree::
   :maxdepth: 1

   workflows
   configuration

**Task-oriented guides** for specific goals:

:doc:`workflows`
    Real-world usage patterns including CI/CD, Python integration, monorepos, and platform-specific scenarios.
    Copy-paste ready examples for common tasks.

:doc:`configuration`
    Complete reference for configuration files (``.bunenvrc``, ``setup.cfg``), environment variables,
    and command-line options. Learn to customize bunenv for your needs.

Advanced Topics
---------------

.. toctree::
   :maxdepth: 1

   advanced
   troubleshooting

:doc:`advanced`
    Deep dives into binary variants, GitHub API integration, custom activation scripts,
    offline installations, security considerations, and edge cases.

:doc:`troubleshooting`
    Solutions to common problems, error messages explained, platform-specific issues,
    and diagnostic techniques. Your first stop when things don't work.

Contributing
------------

.. toctree::
   :maxdepth: 1

   contributing

:doc:`contributing`
    Development setup, coding guidelines, testing, documentation, and the pull request process.
    Everything you need to contribute to bunenv.

Additional Resources
--------------------

.. toctree::
   :maxdepth: 1

   comparison
   migrating

:doc:`comparison`
    How bunenv compares to nodeenv, asdf, mise, and other version managers.
    Understand bunenv's unique value proposition.

:doc:`migrating`
    Migrate from nodeenv, system Bun, or Docker-based workflows to bunenv.
    Step-by-step migration guides with examples.

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

   # Activate
   source myenv/bin/activate             # macOS/Linux
   myenv\Scripts\activate.bat            # Windows cmd
   myenv\Scripts\Activate.ps1            # Windows PowerShell

   # Use Bun
   bun --version
   bun init
   bun install

   # Deactivate
   deactivate_bun

Configuration Files
~~~~~~~~~~~~~~~~~~~

**User defaults** (``~/.bunenvrc``):

.. code-block:: ini

   [bunenv]
   bun = latest
   github_token = ghp_your_token_here

**Project version** (``.bun-version``):

.. code-block:: text

   1.3.3

**Project config** (``setup.cfg`` or ``tox.ini``):

.. code-block:: ini

   [bunenv]
   bun = 1.3.3
   variant = baseline

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

When activated, bunenv sets:

- ``BUN_VIRTUAL_ENV`` - Environment path
- ``BUN_INSTALL`` - Bun installation directory
- ``BUN_INSTALL_BIN`` - Binary directory
- ``PATH`` - Prepended with bin directory

Documentation Organization
--------------------------

This documentation follows the `Diátaxis framework <https://diataxis.fr/>`_:

**Tutorials** (Learning-oriented)
    Step-by-step lessons for newcomers. Start here if you're new to bunenv.

**How-To Guides** (Task-oriented)
    Recipes for specific goals. Use these when you know what you want to achieve.

**Reference** (Information-oriented)
    Technical descriptions of bunenv's machinery. Use for looking up specific details.

**Explanation** (Understanding-oriented)
    Background and context. Use to deepen your understanding of concepts.

Finding What You Need
---------------------

**I want to...**

...get started quickly
    → :doc:`quickstart`

...set up CI/CD
    → :doc:`workflows` → CI/CD Integration

...fix an error
    → :doc:`troubleshooting`

...use with Python
    → :doc:`workflows` → Python Integration

...understand all options
    → :doc:`configuration`

...contribute code
    → :doc:`contributing`

...compare with other tools
    → :doc:`comparison`

**I'm wondering...**

...how bunenv works internally
    → :doc:`advanced` → Understanding the Activation Mechanism

...which variant I need
    → :doc:`advanced` → Binary Variants Deep Dive

...how to migrate from X
    → :doc:`migrating`

...why my environment isn't activating
    → :doc:`troubleshooting` → Activation Issues

Need More Help?
---------------

Can't find what you're looking for?

📖 **Use the search** box at the top of this page

🐛 **Report issues**: `GitHub Issues <https://github.com/JacobCoffee/bunenv/issues>`_

💬 **Ask questions**: `GitHub Discussions <https://github.com/JacobCoffee/bunenv/discussions>`_

📚 **API Reference**: :doc:`../api/index` for technical details

🔧 **CLI Reference**: :doc:`../api/cli` for all command-line options

External Resources
------------------

- **Bun Documentation**: https://bun.sh/docs
- **nodeenv** (inspiration): https://github.com/ekalinin/nodeenv
- **GitHub Repository**: https://github.com/JacobCoffee/bunenv
- **PyPI Package**: https://pypi.org/project/bunenv/
