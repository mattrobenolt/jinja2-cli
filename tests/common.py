#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Common helper classes and functions used by test cases
"""

import subprocess
import sys

from jinja2 import nodes
from jinja2.ext import Extension

from jinja2cli import cli


class UpperCaseExtension(Extension):
    """A custom jinja2 extension that adds a new tag `upperrcase`,
    an upper case block capitalizes all text an variables within
    the block.

    example:
        ```template.j2
        ..
        {% uppercase %}{{foo}}{% enduppercase %}
        ..
        ```

        ```
        >>> import jinja2
        >>> from common import UpperCaseExtension

        >>> env = jinja2.Environment(extensions=[UpperCaseExtension])
        >>> loader = jinja2.FileSystemLoader("path/to/templates/dir")
        >>> template = loader.load(env, "template.j2")
        >>> render = template.render(foo="bar")
        >>> print(render)
        BAR
        ```
    """

    tags = {"uppercase"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = []  # the uppercase tag doesn't require any arguments
        body = parser.parse_statements(["name:enduppercase"], drop_needle=True)
        ret = nodes.CallBlock(
            self.call_method("_uppercase", args), [], [], body
        ).set_lineno(lineno)
        return ret

    def _uppercase(self, caller=None):
        if caller is not None:
            return caller().upper()
        return ""


class CliOpts(object):
    """A helper class to mimic jinja2cli.cli options (passed from optparse)"""

    def __init__(self, **opts):
        self.format = opts.get("format", None)
        self.D = opts.get("D", None)
        self.extensions = opts.get("extensions", [])
        self.section = opts.get("section", None)
        self.outfile = opts.get("outfile", None)
        self.strict = opts.get("strict", False)


def is_python_version(major, minor=None):
    if minor is None:
        return sys.version_info.major == major
    return sys.version_info[:2] == (major, minor)


def to_unicode(string):
    if is_python_version(3):
        return bytes(string, "utf-8")
    else:
        return unicode(string)


def run_jinja2(template, datafile="", args=None, input_data=""):
    """Run jinja2 with the given template, path to data file, input_data and other options, capture the error and output streams and return them"""

    cmd_args = [template]

    if datafile:
        cmd_args.append(datafile)

    if args:
        cmd_args.extend(list(args))

    proc = subprocess.Popen(
        ["jinja2"] + cmd_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if input_data:
        out, err = proc.communicate(input=to_unicode(input_data))
    else:
        out, err = proc.communicate()

    try:
        proc.terminate()
    except OSError:
        pass

    return cli.force_text(out), cli.force_text(err)
