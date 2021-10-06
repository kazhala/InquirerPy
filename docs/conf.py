import os
import sys

sys.path.insert(0, os.path.abspath("."))

project = "InquirerPy"
copyright = "2021, Kevin Zhuang"
author = "Kevin Zhuang"
version = "0.2.4"
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.todo",
    "furo",
    "myst_parser",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "InquirerPy"

napoleon_include_init_with_doc = True
autosectionlabel_prefix_document = True
autodoc_typehints = "signature"
autodoc_member_order = "bysource"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "prompt_toolkit": ("https://python-prompt-toolkit.readthedocs.io/en/master/", None),
    "pfzy": ("https://pfzy.readthedocs.io/en/latest/", None),
}
