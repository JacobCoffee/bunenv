Contributing to bunenv
======================

Thank you for considering contributing to bunenv! This guide will help you get started.

Ways to Contribute
------------------

You don't need to be a coding expert to contribute:

Documentation
~~~~~~~~~~~~~

- Fix typos or unclear explanations
- Add examples for common use cases
- Improve error messages
- Translate documentation

Bug Reports
~~~~~~~~~~~

- Report issues you encounter
- Provide reproduction steps
- Test and verify fixes

Feature Requests
~~~~~~~~~~~~~~~~

- Suggest new features
- Describe your use case
- Discuss implementation approaches

Code Contributions
~~~~~~~~~~~~~~~~~~

- Fix bugs
- Implement new features
- Improve performance
- Add tests

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

You'll need:

- **Python 3.10+** (bunenv's minimum version)
- **Git** for version control
- **uv** (recommended) or pip for package management
- **Make** (optional) for convenience commands

Clone the Repository
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Fork on GitHub first, then:
   git clone https://github.com/YOUR-USERNAME/bunenv.git
   cd bunenv

Install in Development Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using uv (Recommended)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Sync all dependencies including dev tools
   uv sync

   # Install bunenv in editable mode
   uv pip install -e .

   # Verify it works
   uv run bunenv --version

Using pip
^^^^^^^^^

.. code-block:: bash

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows

   # Install in editable mode with dev dependencies
   pip install -e ".[dev]"

   # Verify it works
   bunenv --version

Project Structure
-----------------

Understanding the Layout
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   bunenv/
   ├── src/bunenv/
   │   ├── __init__.py      # Main module (all code here!)
   │   └── py.typed         # PEP 561 type marker
   ├── tests/               # Test suite
   │   ├── test_*.py        # Unit tests
   │   └── conftest.py      # Pytest configuration
   ├── docs/                # Documentation
   │   ├── source/          # Sphinx source files
   │   └── Makefile         # Build documentation
   ├── .github/
   │   └── workflows/       # CI/CD pipelines
   ├── pyproject.toml       # Project metadata
   ├── README.md            # GitHub README
   └── LICENSE              # BSD-3-Clause license

Key Design Principles
~~~~~~~~~~~~~~~~~~~~~

1. **Single-file module**: All code in ``src/bunenv/__init__.py``
2. **Zero dependencies**: Pure Python stdlib only
3. **nodeenv compatibility**: Maintain similar architecture
4. **Cross-platform**: Support macOS, Linux, Windows
5. **Minimal changes**: Keep close to nodeenv's proven design

Making Changes
--------------

Create a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create branch from main
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name

Development Workflow
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Make changes to src/bunenv/__init__.py

   # Test locally
   uv run bunenv /tmp/test-env --bun=latest
   source /tmp/test-env/bin/activate
   bun --version
   deactivate_bun

   # Run linters
   uv run ruff check src/
   uv run ruff format src/

   # Run tests
   uv run pytest

   # Check coverage
   uv run pytest --cov=src/bunenv --cov-report=html

Code Style Guidelines
---------------------

We use Ruff for linting and formatting.

Python Style
~~~~~~~~~~~~

.. code-block:: python

   # Good: Clear, documented, follows nodeenv patterns
   def get_bun_versions() -> list[str]:
       """Return all available Bun versions.

       Fetches version list from GitHub Releases API.

       Returns:
           List of version strings (e.g., ['1.3.3', '1.3.2', ...])
       """
       return [dct["version"] for dct in _get_versions_json()]

   # Bad: Unclear, undocumented
   def get_vers():
       return [d["v"] for d in get_json()]

Key Conventions
~~~~~~~~~~~~~~~

**Naming**:

.. code-block:: python

   # Functions: snake_case
   def download_bun_bin(url: str) -> None: ...

   # Constants: UPPER_SNAKE_CASE
   ACTIVATE_SH: str = """..."""

   # Variables: snake_case
   bun_version: str = "1.3.3"

**Type Hints** (preferred but not required):

.. code-block:: python

   # Modern union syntax (Python 3.10+)
   def get_env_dir(args: argparse.Namespace) -> str | None: ...

   # Not: Optional[str], Union[str, None]

**Line Length**: 120 characters

**Docstrings**: Google style (like nodeenv)

.. code-block:: python

   def example_function(param1: str, param2: int = 42) -> dict:
       """Short one-line summary.

       Longer description explaining what this does,
       why it exists, and any important caveats.

       Args:
           param1: Description of parameter
           param2: Description with default

       Returns:
           Description of return value

       Raises:
           ValueError: When this happens
       """

Running Quality Checks
----------------------

Before Committing
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all quality checks
   uv run ruff check src/
   uv run ruff format src/

   # Run tests
   uv run pytest

   # Check coverage (aim for >95%)
   uv run pytest --cov=src/bunenv --cov-report=term-missing

Fix Lint Errors
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Auto-fix what's possible
   uv run ruff check --fix src/

   # Format code
   uv run ruff format src/

   # Check again
   uv run ruff check src/

Writing Tests
-------------

Test Organization
~~~~~~~~~~~~~~~~~

Tests live in ``tests/`` and follow this structure:

.. code-block:: text

   tests/
   ├── conftest.py              # Fixtures
   ├── test_version_parsing.py  # Version utilities
   ├── test_url_construction.py # URL building
   ├── test_environment.py      # Environment creation
   └── test_cli.py              # Command-line interface

Writing a Test
~~~~~~~~~~~~~~

.. code-block:: python

   # tests/test_example.py
   import pytest
   from bunenv import parse_version, get_bun_bin_url

   def test_parse_version_basic():
       """Test basic version parsing"""
       assert parse_version("1.3.3") == (1, 3, 3)
       assert parse_version("v1.3.3") == (1, 3, 3)
       assert parse_version("bun-v1.3.3") == (1, 3, 3)

   def test_parse_version_invalid():
       """Test invalid version handling"""
       assert parse_version("invalid") == ()

   @pytest.mark.parametrize("version,expected", [
       ("1.3.3", (1, 3, 3)),
       ("2.0.0", (2, 0, 0)),
       ("invalid", ()),
   ])
   def test_parse_version_parametrized(version, expected):
       """Test multiple cases"""
       assert parse_version(version) == expected

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # All tests
   uv run pytest

   # Specific test file
   uv run pytest tests/test_version_parsing.py

   # Specific test
   uv run pytest tests/test_version_parsing.py::test_parse_version_basic

   # With coverage
   uv run pytest --cov=src/bunenv

   # Verbose output
   uv run pytest -v

   # Stop on first failure
   uv run pytest -x

Test Fixtures
~~~~~~~~~~~~~

Use fixtures for common setup:

.. code-block:: python

   # conftest.py
   import pytest
   import tempfile
   from pathlib import Path

   @pytest.fixture
   def temp_env_dir():
       """Provide temporary directory for test environments"""
       with tempfile.TemporaryDirectory() as tmpdir:
           yield Path(tmpdir)

   # test_example.py
   def test_create_environment(temp_env_dir):
       """Test environment creation"""
       from bunenv import create_environment
       import argparse

       args = argparse.Namespace(
           bun="1.3.3",
           variant="",
           python_virtualenv=False,
           # ... other required args
       )

       create_environment(str(temp_env_dir), args)
       assert (temp_env_dir / "bin" / "bun").exists()

Documentation Changes
---------------------

Building Documentation Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install docs dependencies
   uv sync --group docs

   # Build HTML docs
   cd docs
   uv run make html

   # View in browser
   open build/html/index.html  # macOS
   xdg-open build/html/index.html  # Linux
   start build/html/index.html  # Windows

Documentation Style
~~~~~~~~~~~~~~~~~~~

Follow these guidelines:

**Headers**:

.. code-block:: rst

   Main Title
   ==========

   Section
   -------

   Subsection
   ~~~~~~~~~~

   Sub-subsection
   ^^^^^^^^^^^^^^

**Code Blocks**:

.. code-block:: rst

   .. code-block:: bash

      # Comment explaining what this does
      bunenv .venv --bun=1.3.3

   .. code-block:: python

      # Python example
      import bunenv
      bunenv.main()

**Admonitions**:

.. code-block:: rst

   .. note::
      Helpful information

   .. warning::
      Something to watch out for

   .. tip::
      Pro tip for efficiency

   .. important::
      Critical information

   .. danger::
      Serious warning

**Cross-References**:

.. code-block:: rst

   See :doc:`workflows` for examples.
   Refer to :func:`bunenv.get_bun_versions`.
   Check :ref:`installation-guide`.

Submitting Changes
------------------

Commit Messages
~~~~~~~~~~~~~~~

Follow Conventional Commits:

.. code-block:: bash

   # Format: <type>: <description>

   feat: add support for Bun variant selection
   fix: correct architecture detection on ARM Macs
   docs: improve quickstart tutorial
   test: add tests for URL construction
   refactor: simplify version parsing logic
   build: update dependencies
   ci: add Windows to test matrix

**Types**:

- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation only
- ``test``: Test changes
- ``refactor``: Code refactoring
- ``build``: Build system changes
- ``ci``: CI/CD changes
- ``bump``: Version bumps

**Examples**:

.. code-block:: bash

   # Good
   git commit -m "feat: add --clean-src option to save disk space"
   git commit -m "fix: resolve musl detection on Alpine Linux"
   git commit -m "docs: add troubleshooting section for rate limits"

   # Bad
   git commit -m "fixed stuff"
   git commit -m "WIP"
   git commit -m "asdf"

Push and Create Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push your branch
   git push origin feature/your-feature-name

   # Create PR on GitHub
   # Or use GitHub CLI:
   gh pr create --title "Add feature X" --body "Description of changes"

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

Your PR should:

✓ **Have a clear title**: Describe what it does

✓ **Include description**: Explain why the change is needed

✓ **Reference issues**: Use "Fixes #123" or "Closes #456"

✓ **Pass all checks**: CI must be green

✓ **Include tests**: For new features or bug fixes

✓ **Update docs**: If behavior changes

**PR Template**:

.. code-block:: markdown

   ## Description
   Brief description of what this PR does.

   ## Motivation
   Why is this change needed? What problem does it solve?

   ## Changes
   - Added X
   - Modified Y
   - Fixed Z

   ## Testing
   How did you test this?
   - [ ] Local testing
   - [ ] Added unit tests
   - [ ] Tested on macOS/Linux/Windows

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Tests pass locally
   - [ ] Documentation updated
   - [ ] Commit messages follow convention

   ## Related Issues
   Fixes #123

Review Process
--------------

What to Expect
~~~~~~~~~~~~~~

1. **Automated checks run**: Linting, tests, builds
2. **Maintainer review**: Usually within a few days
3. **Feedback and iteration**: Address review comments
4. **Approval and merge**: Once everything looks good

Responding to Review
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Make requested changes
   # Edit files...

   # Commit changes
   git add .
   git commit -m "Address review feedback"

   # Push to update PR
   git push origin feature/your-feature-name

Common Review Feedback
~~~~~~~~~~~~~~~~~~~~~~

- "Add tests for this code"
- "Update docstring to explain X"
- "Extract this into a separate function"
- "Follow naming convention (snake_case)"
- "Add type hints"

Don't take it personally - reviews help improve code quality!

Release Process
---------------

(For Maintainers)

Version Bumping
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update version in src/bunenv/__init__.py
   bunenv_version: str = "0.2.0"

   # Update pyproject.toml
   version = "0.2.0"

   # Commit
   git commit -am "bump: version 0.2.0"

   # Tag
   git tag -a v0.2.0 -m "Release v0.2.0"

   # Push
   git push origin main --tags

Creating Release
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create GitHub release (triggers publish workflow)
   gh release create v0.2.0 \
     --title "bunenv v0.2.0" \
     --notes "$(git log --oneline v0.1.0..HEAD)"

This automatically:

1. Builds package with uv
2. Publishes to PyPI via trusted publishing
3. Updates documentation

Trusted Publishing
~~~~~~~~~~~~~~~~~~

bunenv uses PyPI's trusted publishing:

- No manual token needed
- GitHub Actions OIDC authentication
- Configured in PyPI project settings

Getting Help
------------

Questions About Contributing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **GitHub Discussions**: https://github.com/JacobCoffee/bunenv/discussions
- **Open an Issue**: Tag with "question"
- **Check nodeenv**: bunenv follows nodeenv patterns

Stuck on Something?
~~~~~~~~~~~~~~~~~~~

Don't hesitate to ask! Open a draft PR with:

.. code-block:: markdown

   ## Work in Progress

   I'm working on X but need help with Y.

   Current status:
   - [x] Did this
   - [ ] Stuck on this

   Questions:
   - How should I approach Z?

Contributor Recognition
-----------------------

All contributors are recognized in:

- GitHub contributors page
- Release notes
- Documentation credits

Your contributions, big or small, are valued!

Code of Conduct
---------------

Be Respectful
~~~~~~~~~~~~~

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

Not Acceptable
~~~~~~~~~~~~~~

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

Enforcement
~~~~~~~~~~~

Violations can be reported to the project maintainers.

Advanced Topics
---------------

Working with nodeenv Codebase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since bunenv is adapted from nodeenv:

.. code-block:: bash

   # Clone nodeenv for reference
   git clone https://github.com/ekalinin/nodeenv.git ../nodeenv

   # Compare implementations
   diff -u ../nodeenv/nodeenv.py src/bunenv/__init__.py

When adapting nodeenv code:

1. Credit original author in commits
2. Maintain similar structure
3. Adapt for Bun-specific needs (GitHub API, etc.)
4. Document differences

Testing Across Platforms
~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub Actions tests on:

- Ubuntu (Linux glibc)
- macOS (Intel and ARM)
- Windows

For local cross-platform testing:

.. code-block:: bash

   # Docker for Linux variants
   docker run -it --rm -v $(pwd):/bunenv python:3.11-alpine
   cd /bunenv && pip install -e . && bunenv /tmp/test --bun=latest

   # Test musl variant
   docker run -it --rm -v $(pwd):/bunenv python:3.11-alpine

Performance Profiling
~~~~~~~~~~~~~~~~~~~~~

If working on performance:

.. code-block:: bash

   # Profile environment creation
   python -m cProfile -o profile.stats -m bunenv /tmp/test --bun=1.3.3

   # Analyze
   python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

Next Steps
----------

Ready to contribute?

1. Fork the repository
2. Set up development environment
3. Find an issue to work on (look for "good first issue" label)
4. Create a branch and start coding
5. Submit a pull request

Thank you for contributing to bunenv!
