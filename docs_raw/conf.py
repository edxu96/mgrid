"""Configuration file for documentation with sphinx."""
from datetime import date
import os
import sys

sys.path.insert(0, os.path.abspath("~/GitHub/mgrid/mgrid"))

project = "mgrid"
copyright = f"2020-{date.today().year}, Edward Xu"  # noqa: A001
author = "Edward Xu"

# The full version, including alpha/beta/rc tags
release = "v0.2.2"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
source_encoding = "utf-8"

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = True
