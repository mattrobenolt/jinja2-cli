#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest

from jinja2cli import cli

from .common import run_jinja2

TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files/template.j2"
)

DATA_W_SECTIONS = (
    """{"title_data": {"title": "foo"}, "other_data": {"title": "bar"}}"""
)


def test_section_short():
    out, err = run_jinja2(
        TEMPLATE, args=("-s", "title_data"), input_data=DATA_W_SECTIONS
    )
    assert "" == err
    assert "foo" == out


def test_section_long():
    out, err = run_jinja2(
        TEMPLATE, args=("--section", "title_data"), input_data=DATA_W_SECTIONS
    )
    assert "" == err
    assert "foo" == out
