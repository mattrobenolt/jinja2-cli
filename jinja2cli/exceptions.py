#!/usr/bin/python
# -*- coding: utf-8 -*-

class InvalidDataFormat(Exception): pass
class InvalidInputData(Exception): pass

class MalformedINI(InvalidInputData): pass
class MalformedJSON(InvalidInputData): pass
class MalformedQuerystring(InvalidInputData): pass
class MalformedTOML(InvalidDataFormat): pass
class MalformedYAML(InvalidInputData): pass

if __name__ == '__main__':
    raise RuntimeError('This is not an executable module.')