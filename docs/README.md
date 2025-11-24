# bunenv Documentation

This directory contains the Sphinx documentation for bunenv.

## Building the Documentation

### Prerequisites

Install documentation dependencies:

```bash
uv sync --group docs
```

### Build HTML Documentation

```bash
# From the docs/ directory
make html

# Or from the project root
cd docs && make html
```

The built documentation will be in `docs/_build/html/`. Open `docs/_build/html/index.html` in your browser to view it.

### Build Other Formats

```bash
# PDF (requires LaTeX)
make latexpdf

# EPUB
make epub

# Plain text
make text

# See all available formats
make help
```

### Clean Build Artifacts

```bash
# Clean standard build artifacts
make clean

# Clean everything including generated files
make clean-all
```

## Documentation Structure

```
docs/
├── source/
│   ├── conf.py              # Sphinx configuration
│   ├── index.rst            # Main documentation index
│   ├── api/                 # API reference documentation
│   │   └── index.rst        # API docs index
│   ├── guides/              # User guides and tutorials
│   │   └── index.rst        # Guides index
│   └── _static/             # Static files (CSS, images, etc.)
├── Makefile                 # Build automation (Unix)
├── make.bat                 # Build automation (Windows)
└── README.md                # This file
```

## Writing Documentation

### ReStructuredText Basics

The documentation uses reStructuredText (`.rst`) format. Here are some basics:

```rst
Section Title
=============

Subsection
----------

**bold text**
*italic text*
``code``

- Bullet list
- Item 2

1. Numbered list
2. Item 2

.. code-block:: python

   def example():
       return "Hello"

.. note::
   This is a note admonition.

.. warning::
   This is a warning admonition.
```

### Markdown Support

MyST Parser is configured, so you can also use Markdown (`.md`) files:

```markdown
# Section Title

## Subsection

**bold text**
*italic text*
`code`

- Bullet list
- Item 2

\```python
def example():
    return "Hello"
\```
```

### API Documentation

API documentation is auto-generated from docstrings using Sphinx autodoc:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """Brief description of the function.

    Detailed description can go here.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Cross-References

Reference other parts of the documentation:

```rst
See :func:`bunenv.create_environment` for details.
See :class:`bunenv.Config` for configuration options.
See :doc:`guides/index` for user guides.
```

## Sphinx Extensions

The documentation uses these Sphinx extensions:

- **sphinx.ext.autodoc**: Auto-generate API docs from docstrings
- **sphinx.ext.napoleon**: Support for Google-style docstrings
- **sphinx.ext.viewcode**: Add links to source code
- **sphinx.ext.intersphinx**: Link to other projects' documentation
- **sphinx_autodoc_typehints**: Better type hint rendering
- **sphinx_copybutton**: Add copy button to code blocks
- **myst_parser**: Markdown support

## Theme

The documentation uses the [Read the Docs theme](https://sphinx-rtd-theme.readthedocs.io/).

Theme options are configured in `source/conf.py`:

```python
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "sticky_navigation": True,
    "navigation_depth": 4,
    # ... other options
}
```

## Live Reload (Development)

For live reloading during documentation development, install `sphinx-autobuild`:

```bash
uv pip install sphinx-autobuild
```

Then run:

```bash
make livehtml
```

This will serve the documentation at http://127.0.0.1:8000 and automatically rebuild when you save changes.

## Contributing to Documentation

1. **For API docs**: Update docstrings in the source code
2. **For guides**: Edit files in `source/guides/`
3. **For structure**: Edit `source/index.rst` or add new `.rst` files

When adding new pages:

1. Create the `.rst` or `.md` file in the appropriate directory
2. Add it to the `toctree` directive in the parent index file
3. Rebuild the documentation to verify

## Troubleshooting

### Import Errors

If Sphinx can't import the bunenv module:

```bash
# Ensure bunenv is installed in development mode
uv pip install -e .
```

### Build Warnings

Fix warnings by:

1. Checking docstring formatting
2. Ensuring all cross-references are valid
3. Verifying file paths in toctree directives

### Missing Dependencies

If you get errors about missing packages:

```bash
# Reinstall docs dependencies
uv sync --group docs
```

## Documentation Standards

- Keep line length under 120 characters
- Use clear, concise language
- Include code examples where appropriate
- Cross-reference related sections
- Keep the structure organized and navigable
- Test all code examples to ensure they work
- Update documentation when changing code

## Publishing Documentation

Documentation can be published to:

- **Read the Docs**: https://readthedocs.org/
- **GitHub Pages**: Via `.github/workflows/docs.yml` (if configured)
- **PyPI**: The README.md is used on PyPI

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
