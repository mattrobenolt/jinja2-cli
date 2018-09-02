"""
jinja2cli.filters
==========
Custom jinja filters that extend the Jinja2 dictionary of filters.

License: BSD, see LICENSE for more details.
"""
from sys import version_info
from base64 import b64encode, b64decode

PY3 = version_info[0] == 3


def do_b64_encode(value):
    if PY3:
        return b64encode(value.encode()).decode()
    else:
        return b64encode(value)


def do_b64_decode(value):
    if PY3:
        return b64decode(value.encode()).decode()
    else:
        return b64decode(value)


FILTERS = {
    'b64encode': do_b64_encode,
    'b64decode': do_b64_decode,
}
