#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
jinja2-cli
==========

License: BSD, see LICENSE for more details.
"""

import os
import sys
import logging
from collections import namedtuple
from optparse import OptionParser

import jinja2
from jinja2 import Environment, FileSystemLoader

from jinja2cli import __version__
from jinja2cli.exceptions import *

logger = logging.getLogger(__name__)

# determine the python version we're using
major, minor, micro, _, _ = sys.version_info
IS_PY3 = major == 3
IS_PY2 = major == 2

if IS_PY3:
    # Python 3
    binary_type = bytes

else:
    # Python 2
    binary_type = str

DEFAULT_FORMATTER = 'json'
AVAILABLE_INPUT_FORMATS = [
    'auto', 'json', 'ini', 'toml', 'yaml', 'querystring'
]

ParserObj = namedtuple('ParserObj', 'loader decode_error custom_error')

# ======

def available_formats():
    return sorted(AVAILABLE_INPUT_FORMATS)

def load_available_formats(request_format=None):
    """ Lazy Load the different parsers based on the `request_format`
        determined from the command line arguments.

    :param request_format: The file format of our input settings
    :return:               Dictionary of tuples representing available parsers.
    """

    def attempt_null():
        return ParserObj(lambda x: x, Exception, NotImplementedError)

    def attempt_ini():
        """Determine if ConfigParser is available."""
        if IS_PY3:
            import configparser as ConfigParser
        else: # IS_PY2
            import ConfigParser

        import StringIO

        def parse_ini(data):
            class CustomConfigParser(ConfigParser.ConfigParser):
                def as_dict(self):
                    d = dict(self._sections)
                    for k in d.keys():
                        d[k] = dict(self._defaults, **d[k])
                        d[k].pop('__name__', None)
                    return d
            parser = CustomConfigParser()
            parser.read_file(StringIO.StringIO(data))
            return parser.as_dict()

        return ParserObj(parse_ini, ConfigParser.Error, MalformedINI)

    def attempt_json():
        """Determine if JSON is available."""
        try:
            import simplejson as json
            json_err = json.decoder.JSONDecodeError
        except ImportError:
            import json
            json_err = json.JSONDecodeError
        finally:
            return ParserObj(json.loads, json_err, MalformedJSON)

    def attempt_toml():
        """Determine if TOML is usable."""
        try:
            import toml
        except ImportError as e:
            logger.error(e.message)
            raise EnvironmentError('Missing PyTOML module for TOML config parsing!')
        finally:
            return ParserObj(toml.loads, Exception, MalformedTOML)

    def attempt_yaml():
        """Determine if YAML is usable."""
        try:
            import yaml
        except ImportError as e:
            logger.error(e.message)
            raise EnvironmentError('Missing PyYAML module for YAML config parsing!')
        finally:
            return ParserObj(yaml.load, yaml.YAMLError, MalformedYAML)

    def attempt_querystring():
        """Determine if QueryString is usable."""
        if IS_PY3:
            import urllib.parse as urlparse
        else: # IS_PY2
            import urlparse

        def parse_qs(data):
            ret_dict = {}

            for key, val in urlparse.parse_qs(data).items():
                if not hasattr(val, '__iter__'):
                    val = [val]

                if not val:
                    continue

                val = map(lambda x: x.strip(), val)
                val = val[0] if len(val) == 1 else val

                if '.' in key:
                    pieces = key.split('.')
                    tmp_dict = ret_dict

                    for piece in pieces:
                        slot = val if len(pieces) == 1 else {}
                        sub_piece = tmp_dict.setdefault(piece, slot)

                        if isinstance(sub_piece, dict):
                            tmp_dict = sub_piece
                else:
                    ret_dict[key] = val
            return ret_dict
        return ParserObj(parse_qs, Exception, MalformedQuerystring)

    # conversion matrix
    mapped_fns = {
        'ini': attempt_ini,
        'json': attempt_json,
        'js': attempt_json,
        'querystring': attempt_querystring,
        'qs': attempt_querystring,
        'toml': attempt_toml,
        'yaml': attempt_yaml,
        'yml': attempt_yaml,
    }

    # set the `auto` to whatever is defined as the DEFAULT_FORMATTER
    # recommended is JSON ~ if DEFAULT_FORMATTER is invalid
    # return an `attempt_null` formatter with 1:1 passthrough
    mapped_fns['auto'] = mapped_fns.get(DEFAULT_FORMATTER, attempt_null)

    ALL_FORMATS = set(mapped_fns.keys()).union(set(AVAILABLE_INPUT_FORMATS))

    # ensure that we are always trying to find "something"
    # that we can convert our documents to/from
    if request_format is None:
        request_format = 'auto'

    # if the request_format is a single item, turn it into
    # a list so we can treat it like the global list of
    # "everything" we support
    if request_format not in ALL_FORMATS:
        raise AttributeError('Supplied format is not in available: ' + request_format)

    fn = mapped_fns.get(request_format)
    obj = fn()

    return obj


def render(template_path, data, extensions, strict=False, encoding='utf-8'):
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        extensions=extensions,
        keep_trailing_newline=True
    )

    if strict:
        from jinja2 import StrictUndefined
        env.undefined = StrictUndefined

    # Add environ global
    env.globals['environ'] = os.environ.get

    output = env.get_template(os.path.basename(template_path)).render(data)
    output = output.encode(encoding)

    if isinstance(output, binary_type):
        output = output.decode(encoding)

    return output


def cli(opts, args):
    # grab that formatter from options
    ins_format = opts.format

    if args[1] == '-':  # read from stdin
        data = sys.stdin.read()

    else:
        path = os.path.join(os.getcwd(), os.path.expanduser(args[1]))

        if ins_format == 'auto':
            # convert the automatic type to whatever the file extension was
            ins_format = os.path.splitext(path)[-1].lstrip(' .')

        with open(path, 'r') as f:
            data = f.read()

    # get our parser based on requested type
    parse_obj = load_available_formats(ins_format)

    # locate our template
    template_path = os.path.abspath(args[0])

    try:
        data = parse_obj.loader(data)

    except parse_obj.decode_error as e:
        logger.error(e.message)
        raise parse_obj.custom_error


    extensions = []
    for ext in opts.extensions:
        # Allow shorthand and assume if it's not a module
        # path, it's probably trying to use builtin from jinja2
        if '.' not in ext:
            ext = 'jinja2.ext.' + ext
        extensions.append(ext)

    if opts.D:
        # if there were custom attributes passed from
        # the commandline
        d = {}
        for opt in opts.D:
            key, val = opt.split('=', 1)
            key = key.strip()
            val = val.strip()
            d.setdefault(key, val)

        data.update(d)

    if opts.section:
        # Use only a specific section if needed
        data = data.get(opts.section, {})

    # convert the loaded data into a jinja rendered template
    output = render(template_path, data, extensions, opts.strict)

    # boom baby!
    sys.stdout.write(output)
    sys.exit(0)


def main():
    parser = OptionParser(
        usage="usage: %prog [options] <input template> <input data>",
        version="jinja2-cli v%s\n - Jinja2 v%s" % (
            __version__, jinja2.__version__),
    )
    parser.add_option(
        '--format',
        help='format of input variables: %s' % ', '.join(available_formats()),
        dest='format', action='store', default='auto')
    parser.add_option(
        '-e', '--extension',
        help='extra jinja2 extensions to load',
        dest='extensions', action='append', default=['do'])
    parser.add_option(
        '-D',
        help='Define template variable in the form of key=value',
        action='append', metavar='key=value')
    parser.add_option(
        '-s', '--section',
        help='Use only this section from the configuration',
        dest='section', action='store')
    parser.add_option(
        '--strict',
        help='Disallow undefined variables to be used within the template',
        dest='strict', action='store_true')

    opts, args = parser.parse_args()

    # Dedupe list
    opts.extensions = list(set(opts.extensions))

    if not args or args[0].lower() == 'help' or len(args) == 0:
        parser.print_help()
        sys.exit(1)

    # Without the second argv, assume they want to read from stdin
    if len(args) == 1:
        args.append('-')

    if opts.format.lower() not in AVAILABLE_INPUT_FORMATS + ['auto']:
        raise EnvironmentError('Unsupported format: ' + opts.format)

    # do the parsing
    cli(opts, args)

    # successful exit
    sys.exit(0)



if __name__ == '__main__':
    main()
