#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)


def test_opt_format_auto_implicit(tmp_path):
    datafile = tmp_path / "datafile.env"
    datafile.write_text("title=foo")

    out, err = run_jinja2(TEMPLATE, str(datafile))
    assert "" == err
    assert "foo" == out


def test_opt_format_auto_explicit(tmp_path):
    datafile = tmp_path / "datafile.env"
    datafile.write_text("title=foo")

    out, err = run_jinja2(TEMPLATE, str(datafile), ("-f", "auto"))
    assert "" == err
    assert "foo" == out
