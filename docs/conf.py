# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import charonload

project = charonload.__package__
version = charonload.__version__
release = charonload.__version__
copyright = charonload.__copyright__  # noqa: A001
author = charonload.__author__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_defaultargs",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.moderncmakedomain",
    "myst_parser",
]

# autodoc_member_order = "bysource"
# autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "show-inheritance": True,
    "special-members": "__init__",
    "undoc-members": True,
}

docstring_default_arg_substitution = "*Default*: "
autodoc_preserve_defaults = True

simplify_optional_unions = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "cmake.org": ("https://cmake.org/cmake/help/latest", None),
}
# intersphinx_disabled_reftypes = ["*"]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3


templates_path = ["_templates"]
# exclude_patterns = []

add_module_names = False
coverage_show_missing_items = True

# typehints_defaults = "comma"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

# html_css_files = []

html_copy_source = False
