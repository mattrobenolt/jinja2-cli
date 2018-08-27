"""
jinja2-cli
==========

License: BSD, see LICENSE for more details.
"""

import sys
import os
from jinja2cli import __version__

sys.path.insert(0, os.getcwd())

PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
else:
    text_type = unicode  # NOQA


class InvalidDataFormat(Exception):
    pass


class InvalidInputData(Exception):
    pass


class MalformedJSON(InvalidInputData):
    pass


class MalformedINI(InvalidInputData):
    pass


class MalformedYAML(InvalidInputData):
    pass


class MalformedQuerystring(InvalidInputData):
    pass


class MalformedToml(InvalidDataFormat):
    pass


class MalformedXML(InvalidDataFormat):
    pass


class MalformedEnv(InvalidDataFormat):
    pass


def get_format(fmt):
    try:
        return formats[fmt]()
    except ImportError:
        raise InvalidDataFormat(fmt)


def get_available_formats():
    for fmt in formats.keys():
        try:
            get_format(fmt)
            yield fmt
        except InvalidDataFormat:
            pass
    yield "auto"


def _load_json():
    try:
        import json

        return json.loads, ValueError, MalformedJSON
    except ImportError:
        import simplejson

        return simplejson.loads, simplejson.decoder.JSONDecodeError, MalformedJSON


def _load_ini():
    try:
        import ConfigParser
    except ImportError:
        import configparser as ConfigParser

    def _parse_ini(data):
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO

        class MyConfigParser(ConfigParser.ConfigParser):
            def as_dict(self):
                d = dict(self._sections)
                for k in d:
                    d[k] = dict(self._defaults, **d[k])
                    d[k].pop("__name__", None)
                return d

        p = MyConfigParser()
        p.readfp(StringIO(data))
        return p.as_dict()

    return _parse_ini, ConfigParser.Error, MalformedINI


def _load_yaml():
    import yaml

    return yaml.load, yaml.YAMLError, MalformedYAML


def _load_querystring():
    try:
        import urlparse
    except ImportError:
        import urllib.parse as urlparse

    def _parse_qs(data):
        """ Extend urlparse to allow objects in dot syntax.

        >>> _parse_qs('user.first_name=Matt&user.last_name=Robenolt')
        {'user': {'first_name': 'Matt', 'last_name': 'Robenolt'}}
        """
        dict_ = {}
        for k, v in urlparse.parse_qs(data).items():
            v = map(lambda x: x.strip(), v)
            v = v[0] if len(v) == 1 else v
            if "." in k:
                pieces = k.split(".")
                cur = dict_
                for idx, piece in enumerate(pieces):
                    if piece not in cur:
                        cur[piece] = {}
                    if idx == len(pieces) - 1:
                        cur[piece] = v
                    cur = cur[piece]
            else:
                dict_[k] = v
        return dict_

    return _parse_qs, Exception, MalformedQuerystring


def _load_toml():
    import toml

    return toml.loads, Exception, MalformedToml


def _load_xml():
    import xml
    import xmltodict

    return xmltodict.parse, xml.parsers.expat.ExpatError, MalformedXML


def _load_env():
    def _parse_env(data):
        """
        Parse an envfile format of key=value pairs that are newline separated
        """
        dict_ = {}
        for line in data.splitlines():
            line = line.lstrip()
            # ignore empty or commented lines
            if not line or line[:1] == "#":
                continue
            k, v = line.split("=", 1)
            dict_[k] = v
        return dict_

    return _parse_env, Exception, MalformedEnv


# Global list of available format parsers on your system
# mapped to the callable/Exception to parse a string into a dict
formats = {
    "json": _load_json,
    "ini": _load_ini,
    "yaml": _load_yaml,
    "yml": _load_yaml,
    "querystring": _load_querystring,
    "toml": _load_toml,
    "xml": _load_xml,
    "env": _load_env,
}


import os
import sys
from optparse import OptionParser, Option

import jinja2
from jinja2 import Environment, FileSystemLoader


def render(template_path, data, extensions, strict=False):
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        extensions=extensions,
        keep_trailing_newline=True,
    )
    if strict:
        from jinja2 import StrictUndefined

        env.undefined = StrictUndefined

    # Add environ global
    env.globals["environ"] = os.environ.get

    output = env.get_template(os.path.basename(template_path)).render(data)
    return output.encode("utf-8")


def is_fd_alive(fd):
    if os.name == "nt":
        return not os.isatty(fd.fileno())
    import select

    return bool(select.select([fd], [], [], 0)[0])


def cli(opts, args):
    format = opts.format
    if args[1] == "-":
        if is_fd_alive(sys.stdin):
            data = sys.stdin.read()
        else:
            data = ""
        if format == "auto":
            # default to yaml first if available since yaml
            # is a superset of json
            if "yaml" in formats:
                format = "yaml"
            else:
                format = "json"
    else:
        path = os.path.join(os.getcwd(), os.path.expanduser(args[1]))
        if format == "auto":
            ext = os.path.splitext(path)[1][1:]
            if ext in formats:
                format = ext
            else:
                raise InvalidDataFormat(ext)

        with open(path) as fp:
            data = fp.read()

    template_path = os.path.abspath(args[0])

    if data:
        try:
            fn, except_exc, raise_exc = get_format(format)
        except InvalidDataFormat:
            if format in ("yml", "yaml"):
                raise InvalidDataFormat("%s: install pyyaml to fix" % format)
            if format == "toml":
                raise InvalidDataFormat("toml: install toml to fix")
            if format == "xml":
                raise InvalidDataFormat("xml: install xmltodict to fix")
            raise
        try:
            data = fn(data) or {}
        except except_exc:
            raise raise_exc(u"%s ..." % data[:60])
    else:
        data = {}

    extensions = []
    for ext in opts.extensions:
        # Allow shorthand and assume if it's not a module
        # path, it's probably trying to use builtin from jinja2
        if "." not in ext:
            ext = "jinja2.ext." + ext
        extensions.append(ext)

    data.update(parse_kv_string(opts.D or []))

    # Use only a specific section if needed
    if opts.section:
        section = opts.section
        if section in data:
            data = data[section]
        else:
            sys.stderr.write("ERROR: unknown section. Exiting.")
            return 1

    output = render(template_path, data, extensions, opts.strict)

    if isinstance(output, text_type):
        output = output.encode("utf-8")
    sys.stdout.write(output)
    return 0


def parse_kv_string(pairs):
    return dict(pair.split("=", 1) for pair in pairs)


class LazyHelpOption(Option):
    "An Option class that resolves help from a callable"

    def __setattr__(self, attr, value):
        if attr == "help":
            attr = "_help"
        self.__dict__[attr] = value

    @property
    def help(self):
        h = self._help
        if callable(h):
            h = h()
        # Cache on the class to get rid of the @property
        self.help = h
        return h


def main():
    parser = OptionParser(
        option_class=LazyHelpOption,
        usage="usage: %prog [options] <input template> <input data>",
        version="jinja2-cli v%s\n - Jinja2 v%s" % (__version__, jinja2.__version__),
    )
    parser.add_option(
        "--format",
        help=lambda: "format of input variables: %s"
        % ", ".join(sorted(list(get_available_formats()))),
        dest="format",
        action="store",
        default="auto",
    )
    parser.add_option(
        "-e",
        "--extension",
        help="extra jinja2 extensions to load",
        dest="extensions",
        action="append",
        default=["do", "with_", "autoescape", "loopcontrols"],
    )
    parser.add_option(
        "-D",
        help="Define template variable in the form of key=value",
        action="append",
        metavar="key=value",
    )
    parser.add_option(
        "-s",
        "--section",
        help="Use only this section from the configuration",
        dest="section",
        action="store",
    )
    parser.add_option(
        "--strict",
        help="Disallow undefined variables to be used within the template",
        dest="strict",
        action="store_true",
    )
    opts, args = parser.parse_args()

    # Dedupe list
    opts.extensions = set(opts.extensions)

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    if args[0] == "help":
        parser.print_help()
        sys.exit(1)

    # Without the second argv, assume they want to read from stdin
    if len(args) == 1:
        args.append("-")

    if opts.format not in formats and opts.format != "auto":
        raise InvalidDataFormat(opts.format)

    sys.exit(cli(opts, args))


if __name__ == "__main__":
    main()
