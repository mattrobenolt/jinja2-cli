"""Custom filters for testing"""


def reverse(s):
    """Reverse a string"""
    return s[::-1]


def multiply(value, factor=2):
    """Multiply a value by a factor"""
    return value * factor


def shout(s):
    """Convert string to uppercase with exclamation"""
    return s.upper() + "!"


# Dict of filters that can be imported as a whole
filters = {
    "reverse": reverse,
    "multiply": multiply,
    "shout": shout,
}
