#!/usr/bin/env python3
import importlib.util
import sys

if sys.version_info >= (3, 11):
    sys.exit(0)

sys.exit(0 if importlib.util.find_spec("tomli") else 1)
