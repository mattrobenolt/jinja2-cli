#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest

from jinja2cli import cli

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)


def test_d_variables():
    out, err = run_jinja2(TEMPLATE, args=("-D", "title=foo"))
    assert "" == err
    assert "foo" == out


def test_d_variables_overrides_other_data():
    out, err = run_jinja2(
        TEMPLATE, args=("-D", "title=foo"), input_data="title: bar"
    )
    assert "" == err
    assert "foo" == out
