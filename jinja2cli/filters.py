"""
jinja2cli.filters
==========
Custom jinja filters that extend the Jinja2 dictionary of filters.

License: BSD, see LICENSE for more details.
"""
from base64 import b64encode, b64decode

def do_b64_encode(value):
  return b64encode(value)

def do_b64_decode(value):
  return b64decode(value)

FILTERS = {
  'b64encode':          do_b64_encode,
  'b64decode':          do_b64_decode,
}