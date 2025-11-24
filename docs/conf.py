"""Sphinx configuration for bunenv documentation."""

from __future__ import annotations

import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# Add the src directory to the path so Sphinx can find the bunenv module
docs_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(docs_root / "src"))

# Import bunenv to get version
import bunenv

# -- Project information -----------------------------------------------------
project = "bunenv"
copyright = "2025, Jacob Coffee"
author = "Jacob Coffee"

# The short X.Y version
version = bunenv.bunenv_version
# The full version, including alpha/beta/rc tags
release = bunenv.bunenv_version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "shibuya"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_show_sourcelink = True
html_title = "Docs"

# Theme options for Shibuya
html_context = {
    "source_type": "github",
    "source_user": "JacobCoffee",
    "source_repo": "bunenv",
}

html_theme_options = {
    "logo_target": "/",
    "github_url": "https://github.com/JacobCoffee/bunenv",
    "nav_links": [
        {"title": "PyPI", "url": "https://pypi.org/project/bunenv/"},
    ],
}

# -- Options for autodoc -----------------------------------------------------

# This value contains a list of modules to be mocked up.
autodoc_mock_imports: list[str] = []

# This value selects what content will be inserted into the main body of an
# autoclass directive.
autoclass_content = "both"

# This value selects if automatically documented members are sorted alphabetical
# (value 'alphabetical'), by member type (value 'groupwise') or by source order
# (value 'bysource').
autodoc_member_order = "bysource"

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives.
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

# -- Options for autodoc-typehints -------------------------------------------

# When True, typehints for return types are merged into the description.
typehints_use_rtype = True

# When True, defaults for parameters are merged into the description.
typehints_defaults = "comma"

# -- Options for napoleon ----------------------------------------------------

# Parse Google style docstrings
napoleon_google_docstring = True

# Parse NumPy style docstrings
napoleon_numpy_docstring = False

# Should special members be included in the documentation
napoleon_include_init_with_doc = True

# Use admonition directive for Examples and Notes sections
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True

# -- Options for intersphinx -------------------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for copybutton --------------------------------------------------

# Strip prompt text when copying code blocks
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for MyST --------------------------------------------------------

# Enable extensions for MyST parser
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "substitution",
    "tasklist",
]
