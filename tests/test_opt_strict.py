#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest

from jinja2cli import cli

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)

UNDEFINED_ERROR = "jinja2.exceptions.UndefinedError: 'title' is undefined"


def test_strict_enabled():
    out, err = run_jinja2(TEMPLATE, args=("--strict",))
    assert UNDEFINED_ERROR in err
    assert "" == out


def test_strict_disabled():
    out, err = run_jinja2(TEMPLATE)
    assert "" == err
    assert "" == out
