"""Module with auto-discoverable filter functions"""


def uppercase(s):
    """Convert to uppercase"""
    return s.upper()


def lowercase(s):
    """Convert to lowercase"""
    return s.lower()


def double(n):
    """Double a number"""
    return n * 2


def _private_function(s):
    """This should not be auto-discovered"""
    return "private"
