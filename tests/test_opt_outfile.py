#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest

from jinja2cli import cli

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)


def test_opt_outfile_short(tmp_path):
    outfile = tmp_path / "outfile"
    out, err = run_jinja2(
        TEMPLATE, args=("-o", str(outfile)), input_data="title: foo"
    )

    assert "" == err
    assert "" == out
    assert "foo" == outfile.read_text()


def test_opt_outfile_long(tmp_path):
    outfile = tmp_path / "outfile"
    out, err = run_jinja2(
        TEMPLATE, args=("--outfile", str(outfile)), input_data="title: foo"
    )

    assert "" == err
    assert "" == out
    assert "foo" == outfile.read_text()
