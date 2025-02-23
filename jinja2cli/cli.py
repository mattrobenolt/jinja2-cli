"""
jinja2-cli
==========

License: BSD, see LICENSE for more details.
"""

import warnings

warnings.filterwarnings("ignore")

import os
import sys
from optparse import Option, OptionParser

sys.path.insert(0, os.getcwd())

PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
    bytes_type = bytes
else:
    text_type = unicode  # NOQA
    bytes_type = str  # NOQA


def force_text(data):
    if isinstance(data, text_type):
        return data
    if isinstance(data, bytes_type):
        return data.decode("utf8")
    return data


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


class MalformedHJSON(InvalidDataFormat):
    pass


class MalformedJSON5(InvalidDataFormat):
    pass


def get_format(fmt):
    try:
        return formats[fmt]()
    except ImportError:
        raise InvalidDataFormat(fmt)


def has_format(fmt):
    try:
        get_format(fmt)
        return True
    except InvalidDataFormat:
        return False


def get_available_formats():
    for fmt in formats.keys():
        if has_format(fmt):
            yield fmt
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
        try:
            reader = p.readfp
        except AttributeError:
            reader = p.read_file
        reader(StringIO(data))
        return p.as_dict()

    return _parse_ini, ConfigParser.Error, MalformedINI


def _load_yaml():
    from yaml import load, YAMLError

    try:
        from yaml import CSafeLoader as SafeLoader
    except ImportError:
        from yaml import SafeLoader

    def yaml_loader(stream):
        return load(stream, Loader=SafeLoader)

    return yaml_loader, YAMLError, MalformedYAML


def _load_querystring():
    try:
        import urlparse
    except ImportError:
        import urllib.parse as urlparse

    def _parse_qs(data):
        """Extend urlparse to allow objects in dot syntax.

        >>> _parse_qs('user.first_name=Matt&user.last_name=Robenolt')
        {'user': {'first_name': 'Matt', 'last_name': 'Robenolt'}}
        """
        dict_ = {}
        for k, v in urlparse.parse_qs(data).items():
            v = list(map(lambda x: x.strip(), v))
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
                dict_[force_text(k)] = force_text(v)
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
            dict_[force_text(k)] = force_text(v)
        return dict_

    return _parse_env, Exception, MalformedEnv


def _load_hjson():
    import hjson

    return hjson.loads, Exception, MalformedHJSON


def _load_json5():
    import json5

    return json5.loads, Exception, MalformedJSON5


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
    "hjson": _load_hjson,
    "json5": _load_json5,
}


def render(template_path, data, extensions, strict=False):
    from jinja2 import (
        __version__ as jinja_version,
        Environment,
        FileSystemLoader,
        StrictUndefined,
    )

    # Starting with jinja2 3.1, `with_` and `autoescape` are no longer
    # able to be imported, but since they were default, let's stub them back
    # in implicitly for older versions.
    # We also don't track any lower bounds on jinja2 as a dependency, so
    # it's not easily safe to know it's included by default either.
    if tuple(jinja_version.split(".", 2)) < ("3", "1"):
        for ext in "with_", "autoescape":
            ext = "jinja2.ext." + ext
            if ext not in extensions:
                extensions.append(ext)

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        extensions=extensions,
        keep_trailing_newline=True,
    )
    if strict:
        env.undefined = StrictUndefined

    # Add environ global
    env.globals["environ"] = lambda key: force_text(os.environ.get(key))
    env.globals["get_context"] = lambda: data

    return env.get_template(os.path.basename(template_path)).render(data)


def is_fd_alive(fd):
    if os.name == "nt":
        return not os.isatty(fd.fileno())
    import select

    return bool(select.select([fd], [], [], 0)[0])


def cli(opts, args):
    template_path = args.pop(0)
    format = opts.format

    if len(args) == 0:
        args.append("-")

    data = {}
    for filename in args:
        if filename == "-" and is_fd_alive(sys.stdin):
            data_in = sys.stdin.read()
            # default to yaml first if available since yaml
            # is a superset of json
            if has_format("yaml"):
                data_format = "yaml"
            else:
                data_format = "json"
        else:
            path = os.path.join(os.getcwd(), os.path.expanduser(filename))
            if format == "auto":
                ext = os.path.splitext(path)[1][1:]
                print(f"auto format is {ext}")
                if has_format(ext):
                    data_format = ext
                else:
                    raise InvalidDataFormat(ext)
            else:
                data_format = format

            with open(path) as fp:
                data_in = fp.read()

        template_path = os.path.abspath(template_path)
        if data_in:
            try:
                fn, except_exc, raise_exc = get_format(data_format)
            except InvalidDataFormat:
                if data_format in ("yml", "yaml"):
                    raise InvalidDataFormat("%s: install pyyaml to fix" % data_format)
                if data_format == "toml":
                    raise InvalidDataFormat("toml: install toml to fix")
                if data_format == "xml":
                    raise InvalidDataFormat("xml: install xmltodict to fix")
                if data_format == "hjson":
                    raise InvalidDataFormat("hjson: install hjson to fix")
                if data_format == "json5":
                    raise InvalidDataFormat("json5: install json5 to fix")
                raise
            try:
                data.update(fn(data_in) or {})
            except except_exc:
                raise raise_exc("%s ..." % data_in[:60])

    extensions = []
    for ext in opts.extensions:
        # Allow shorthand and assume if it's not a module
        # path, it's probably trying to use builtin from jinja2
        if "." not in ext:
            ext = "jinja2.ext." + ext
        extensions.append(ext)

    # Use only a specific section if needed
    if opts.section:
        section = opts.section
        if section in data:
            data = data[section]
        else:
            sys.stderr.write("ERROR: unknown section. Exiting.")
            return 1

    data.update(parse_kv_string(opts.D or []))

    if opts.outfile is None:
        out = sys.stdout
    else:
        out = open(opts.outfile, "w")

    if not PY3:
        import codecs

        out = codecs.getwriter("utf8")(out)

    out.write(render(template_path, data, extensions, opts.strict))
    out.flush()
    return 0


def parse_kv_string(pairs):
    dict_ = {}
    for pair in pairs:
        pair = force_text(pair)
        try:
            k, v = pair.split("=", 1)
        except ValueError:
            k, v = pair, None
        dict_[k] = v
    return dict_


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


class LazyOptionParser(OptionParser):
    def __init__(self, **kwargs):
        # Fake a version so we can lazy load it later.
        # This is due to internals of OptionParser, but it's
        # fine
        kwargs["version"] = 1
        kwargs["option_class"] = LazyHelpOption
        OptionParser.__init__(self, **kwargs)

    def get_version(self):
        from jinja2 import __version__ as jinja_version
        from jinja2cli import __version__

        return "jinja2-cli v%s\n - Jinja2 v%s" % (__version__, jinja_version)


def main():
    parser = LazyOptionParser(
        usage="usage: %prog [options] <input template> <input data>"
    )
    parser.add_option(
        "-f",
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
        default=["do", "loopcontrols"],
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
    parser.add_option(
        "-o",
        "--outfile",
        help="File to use for output. Default is stdout.",
        dest="outfile",
        metavar="FILE",
        action="store",
    )
    opts, args = parser.parse_args()

    # Dedupe list
    opts.extensions = set(opts.extensions)

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    # Without the second argv, assume they maybe want to read from stdin
    if len(args) == 1:
        args.append("")

    if opts.format not in formats and opts.format != "auto":
        raise InvalidDataFormat(opts.format)

    sys.exit(cli(opts, args))


if __name__ == "__main__":
    main()
