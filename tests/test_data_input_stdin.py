#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest

from jinja2cli import cli

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)


def test_stdin_implicit_subprocess():
    out, err = run_jinja2(TEMPLATE, input_data="title: foo")
    assert "" == err
    assert "foo" == out


def test_stdin_explicit_subprocess():
    out, err = run_jinja2(TEMPLATE, "-", input_data="title: foo")
    assert "" == err
    assert "foo" == out
