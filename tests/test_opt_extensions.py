#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import pytest

from jinja2cli import cli

from .common import is_python_version, run_jinja2, to_unicode

TEMPLATE_CONTENT = "{% uppercase %}{{title}}{% enduppercase %}"


def test_opt_extensions_short(tmp_path):
    template_file = tmp_path / "template.j2"

    if is_python_version(2):
        template_file.write_text(unicode(TEMPLATE_CONTENT))
    else:
        template_file.write_text(TEMPLATE_CONTENT)

    out, err = run_jinja2(
        str(template_file),
        args=("-e", "common.UpperCaseExtension"),
        input_data="title: foo",
    )

    assert "" == err
    assert "FOO" == out


def test_opt_extensions_long(tmp_path):
    template_file = tmp_path / "template.j2"

    if is_python_version(2):
        template_file.write_text(unicode(TEMPLATE_CONTENT))
    else:
        template_file.write_text(TEMPLATE_CONTENT)

    out, err = run_jinja2(
        str(template_file),
        args=("--extension", "common.UpperCaseExtension"),
        input_data="title: foo",
    )

    assert "" == err
    assert "FOO" == out
