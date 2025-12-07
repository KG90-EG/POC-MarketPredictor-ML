# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
project = 'POC-MarketPredictor-ML'
copyright = '2025, POC-MarketPredictor-ML contributors'
author = 'POC-MarketPredictor-ML contributors'
release = '0.9.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',  # Markdown support
    'sphinx.ext.autodoc',  # Auto-generate docs from docstrings
    'sphinx.ext.viewcode',  # Add links to source code
    'sphinx.ext.napoleon',  # Support for Google/NumPy style docstrings
    'sphinx.ext.intersphinx',  # Link to other projects' docs
    'sphinx.ext.todo',  # Support for TODO items
]

# Markdown support
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': '',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Logo and favicon
# html_logo = "_static/logo.png"
# html_favicon = "_static/favicon.ico"

html_context = {
    "display_github": True,
    "github_user": "KG90-EG",
    "github_repo": "POC-MarketPredictor-ML",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Intersphinx configuration -----------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'fastapi': ('https://fastapi.tiangolo.com', None),
    'react': ('https://react.dev', None),
}

# -- Todo extension ----------------------------------------------------------
todo_include_todos = True
