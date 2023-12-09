#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)


def test_opt_format_short(tmp_path):
    datafile = tmp_path / "datafile.env"
    datafile.write_text("title=foo")

    out, err = run_jinja2(TEMPLATE, str(datafile), ("-f", "env"))
    assert "" == err
    assert "foo" == out


def test_opt_format_long(tmp_path):
    datafile = tmp_path / "datafile.env"
    datafile.write_text("title=foo")

    out, err = run_jinja2(TEMPLATE, str(datafile), ("--format", "env"))
    assert "" == err
    assert "foo" == out
