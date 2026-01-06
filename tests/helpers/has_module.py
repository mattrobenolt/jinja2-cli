#!/usr/bin/env python3
import importlib.util
import sys

if len(sys.argv) != 2:
    sys.stderr.write("Usage: has_module.py <module>\n")
    sys.exit(2)

module = sys.argv[1]
sys.exit(0 if importlib.util.find_spec(module) else 1)
