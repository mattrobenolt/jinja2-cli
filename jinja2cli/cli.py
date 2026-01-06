"""
jinja2-cli
==========

License: BSD, see LICENSE for more details.
"""

import argparse
import importlib
import importlib.util
import os
import sys
from types import ModuleType
from typing import Any, Callable, Iterable, Iterator, List, Optional, Sequence, Tuple, Type, Union


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


ParserFn = Callable[[str], Any]
FormatLoadResult = Tuple[ParserFn, Type[Exception], Type[Exception]]
ExtensionSpec = Union[str, ModuleType, Type[Any]]


def get_format(fmt: str) -> FormatLoadResult:
    try:
        return formats[fmt]()
    except ImportError:
        raise InvalidDataFormat(fmt)


def has_format(fmt: str) -> bool:
    try:
        get_format(fmt)
        return True
    except InvalidDataFormat:
        return False


def get_available_formats() -> Iterator[str]:
    for fmt in formats.keys():
        if has_format(fmt):
            yield fmt
    yield "auto"


def _load_json() -> FormatLoadResult:
    import json

    return json.loads, json.JSONDecodeError, MalformedJSON


def _load_ini() -> FormatLoadResult:
    import configparser

    def _parse_ini(data: str) -> dict:
        from io import StringIO

        class MyConfigParser(configparser.ConfigParser):
            def as_dict(self) -> dict:
                return {section: dict(self.items(section, raw=True)) for section in self.sections()}

        p = MyConfigParser()
        p.read_file(StringIO(data))
        return p.as_dict()

    return _parse_ini, configparser.Error, MalformedINI


def _load_yaml() -> FormatLoadResult:
    from yaml import YAMLError, load

    try:
        from yaml import CSafeLoader as SafeLoader
    except ImportError:
        from yaml import SafeLoader

    def yaml_loader(stream: str) -> Any:
        return load(stream, Loader=SafeLoader)

    return yaml_loader, YAMLError, MalformedYAML


def _load_querystring() -> FormatLoadResult:
    from urllib.parse import parse_qs

    def _parse_qs(data: str) -> dict:
        """Extend urlparse to allow objects in dot syntax.

        >>> _parse_qs('user.first_name=Matt&user.last_name=Robenolt')
        {'user': {'first_name': 'Matt', 'last_name': 'Robenolt'}}
        """
        dict_ = {}
        for k, v in parse_qs(data).items():
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
                dict_[k] = v
        return dict_

    return _parse_qs, Exception, MalformedQuerystring


def _load_toml() -> FormatLoadResult:
    if sys.version_info < (3, 11):
        import tomli as tomllib  # type: ignore[unresolved-import]
    else:
        import tomllib

    return tomllib.loads, Exception, MalformedToml


def _load_xml() -> FormatLoadResult:
    from xml.parsers import expat

    import xmltodict

    return xmltodict.parse, expat.ExpatError, MalformedXML


def _load_env() -> FormatLoadResult:
    def _parse_env(data: str) -> dict:
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


def _load_hjson() -> FormatLoadResult:
    import hjson

    return hjson.loads, Exception, MalformedHJSON


def _load_json5() -> FormatLoadResult:
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


def render(
    template_path: str,
    data: dict,
    extensions: List[ExtensionSpec],
    strict: bool = False,
) -> str:
    from jinja2 import (
        Environment,
        FileSystemLoader,
        StrictUndefined,
    )
    from jinja2 import (
        __version__ as jinja_version,
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
    env.globals["environ"] = lambda key: os.environ.get(key)
    env.globals["get_context"] = lambda: data

    return env.get_template(os.path.basename(template_path)).render(data)


def _split_extension_path(extension: str) -> Tuple[str, Optional[str]]:
    if ":" in extension:
        module_name, object_name = extension.split(":", 1)
        return module_name, object_name or None
    module_name, _, object_name = extension.rpartition(".")
    if module_name:
        return module_name, object_name or None
    return extension, None


def _load_local_module(module_name: str, base_dir: str) -> Optional[ModuleType]:
    module_path = os.path.join(base_dir, *module_name.split("."))
    for candidate in (module_path + ".py", os.path.join(module_path, "__init__.py")):
        if not os.path.isfile(candidate):
            continue
        spec = importlib.util.spec_from_file_location(module_name, candidate)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    return None


def _resolve_extension(extension: ExtensionSpec, base_dir: str) -> ExtensionSpec:
    if not isinstance(extension, str):
        return extension
    if extension.startswith("jinja2.ext."):
        return extension
    module_name, object_name = _split_extension_path(extension)
    if object_name:
        if importlib.util.find_spec(module_name) is not None:
            module = importlib.import_module(module_name)
        else:
            module = _load_local_module(module_name, base_dir)
        if module is None:
            raise ImportError("Cannot import %r" % module_name)
        try:
            return getattr(module, object_name)
        except AttributeError as exc:
            raise ImportError("Cannot import %r from %r" % (object_name, module_name)) from exc
    if importlib.util.find_spec(module_name) is not None:
        return extension
    module = _load_local_module(module_name, base_dir)
    if module is None:
        return extension
    return module


def cli(opts: argparse.Namespace, args: Sequence[str]) -> int:
    template_path, data = args
    format = opts.format
    if data in ("-", ""):
        if data == "-" or (data == "" and not sys.stdin.isatty()):
            data = sys.stdin.read()
        if format == "auto":
            # default to yaml first if available since yaml
            # is a superset of json
            if has_format("yaml"):
                format = "yaml"
            else:
                format = "json"
    else:
        path = os.path.join(os.getcwd(), os.path.expanduser(data))
        if format == "auto":
            ext = os.path.splitext(path)[1][1:]
            if has_format(ext):
                format = ext
            else:
                raise InvalidDataFormat(ext)

        with open(path) as fp:
            data = fp.read()

    template_path = os.path.abspath(template_path)

    if data:
        try:
            fn, except_exc, raise_exc = get_format(format)
        except InvalidDataFormat:
            if format in ("yml", "yaml"):
                raise InvalidDataFormat("%s: install pyyaml to fix" % format)
            if format == "toml":
                raise InvalidDataFormat("toml: install tomli to fix")
            if format == "xml":
                raise InvalidDataFormat("xml: install xmltodict to fix")
            if format == "hjson":
                raise InvalidDataFormat("hjson: install hjson to fix")
            if format == "json5":
                raise InvalidDataFormat("json5: install json5 to fix")
            raise
        try:
            data = fn(data) or {}
        except except_exc:
            raise raise_exc("%s ..." % data[:60])
    else:
        data = {}

    extensions = []
    for ext in opts.extensions:
        # Allow shorthand and assume if it's not a module
        # path, it's probably trying to use builtin from jinja2
        if "." not in ext and ":" not in ext:
            ext = "jinja2.ext." + ext
        extensions.append(_resolve_extension(ext, os.getcwd()))

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

    out.write(render(template_path, data, extensions, opts.strict))
    out.flush()
    return 0


def parse_kv_string(pairs: Iterable[str]) -> dict:
    dict_ = {}
    for pair in pairs:
        try:
            k, v = pair.split("=", 1)
        except ValueError:
            k, v = pair, None
        dict_[k] = v
    return dict_


FORMAT_HELP_SENTINEL = "__JINJA2CLI_FORMAT_HELP__"


class LazyFormatArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        if FORMAT_HELP_SENTINEL in help_text:
            help_text = help_text.replace(
                FORMAT_HELP_SENTINEL,
                "format of input variables: %s" % ", ".join(sorted(list(get_available_formats()))),
            )
        return help_text


class LazyVersionAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: Optional[str] = None,
    ) -> None:
        from jinja2 import __version__ as jinja_version

        from jinja2cli import __version__

        parser.exit(message="jinja2-cli v%s\n - Jinja2 v%s\n" % (__version__, jinja_version))


def main() -> None:
    parser = LazyFormatArgumentParser(usage="%(prog)s [options] <input template> <input data>")
    parser.add_argument(
        "--version",
        action=LazyVersionAction,
        nargs=0,
        help="show program's version number and exit",
    )
    parser.add_argument(
        "-f",
        "--format",
        help=FORMAT_HELP_SENTINEL,
        dest="format",
        default="auto",
    )
    parser.add_argument(
        "-e",
        "--extension",
        help="extra jinja2 extensions to load",
        dest="extensions",
        action="append",
        default=["do", "loopcontrols"],
    )
    parser.add_argument(
        "-D",
        dest="D",
        help="Define template variable in the form of key=value",
        action="append",
        metavar="key=value",
    )
    parser.add_argument(
        "-s",
        "--section",
        help="Use only this section from the configuration",
        dest="section",
    )
    parser.add_argument(
        "--strict",
        help="Disallow undefined variables to be used within the template",
        dest="strict",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="File to use for output. Default is stdout.",
        dest="outfile",
        metavar="FILE",
    )
    parser.add_argument("template", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("data", nargs="?", help=argparse.SUPPRESS)
    opts = parser.parse_args()
    args = [value for value in (opts.template, opts.data) if value is not None]

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
