"""
jinja2-cli
==========

License: BSD, see LICENSE for more details.
"""

__author__ = "Matt Robenolt"

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("jinja2-cli")
except PackageNotFoundError:
    __version__ = "dev"

from .cli import main  # NOQA
