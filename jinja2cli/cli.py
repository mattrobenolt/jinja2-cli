"""
jinja2-cli
==========

License: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import sys
from collections.abc import Iterable, Iterator, Sequence
from types import ModuleType
from typing import Any, Callable, Tuple, Type, Union


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
    except ModuleNotFoundError:
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


def load_json() -> FormatLoadResult:
    import json

    return json.loads, json.JSONDecodeError, MalformedJSON


def load_ini() -> FormatLoadResult:
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


def load_yaml() -> FormatLoadResult:
    from yaml import YAMLError, load

    try:
        from yaml import CSafeLoader as SafeLoader
    except ImportError:
        from yaml import SafeLoader

    def yaml_loader(stream: str) -> Any:
        return load(stream, Loader=SafeLoader)

    return yaml_loader, YAMLError, MalformedYAML


def load_querystring() -> FormatLoadResult:
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


def load_toml() -> FormatLoadResult:
    try:
        import tomllib  # type: ignore[unresolved-import]
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[unresolved-import]

    return tomllib.loads, Exception, MalformedToml


def load_xml() -> FormatLoadResult:
    from xml.parsers import expat

    import xmltodict

    return xmltodict.parse, expat.ExpatError, MalformedXML


def load_env() -> FormatLoadResult:
    def parse_env(data: str) -> dict:
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

    return parse_env, Exception, MalformedEnv


def load_hjson() -> FormatLoadResult:
    import hjson

    return hjson.loads, Exception, MalformedHJSON


def load_json5() -> FormatLoadResult:
    import json5

    return json5.loads, Exception, MalformedJSON5


# Global list of available format parsers on your system
# mapped to the callable/Exception to parse a string into a dict
formats = {
    "json": load_json,
    "ini": load_ini,
    "yaml": load_yaml,
    "yml": load_yaml,
    "querystring": load_querystring,
    "toml": load_toml,
    "xml": load_xml,
    "env": load_env,
    "hjson": load_hjson,
    "json5": load_json5,
}


def render(
    template_path: str,
    data: dict,
    extensions: list[ExtensionSpec],
    strict: bool = False,
    trim_blocks: bool = False,
    lstrip_blocks: bool = False,
    autoescape: bool = False,
    variable_start_string: str | None = None,
    variable_end_string: str | None = None,
    block_start_string: str | None = None,
    block_end_string: str | None = None,
    comment_start_string: str | None = None,
    comment_end_string: str | None = None,
    line_statement_prefix: str | None = None,
    line_comment_prefix: str | None = None,
    newline_sequence: str | None = None,
    search_paths: list[str] | None = None,
) -> str:
    from jinja2 import (
        Environment,
        FileSystemLoader,
        StrictUndefined,
        UndefinedError,
    )

    # Build search paths: template directory first, then any -I paths
    template_dir = os.path.dirname(template_path) or "."
    paths = [template_dir] + (search_paths or [])

    env_kwargs: dict = {
        "loader": FileSystemLoader(paths),
        "extensions": extensions,
        "keep_trailing_newline": True,
        "trim_blocks": trim_blocks,
        "lstrip_blocks": lstrip_blocks,
    }
    if autoescape:
        env_kwargs["autoescape"] = True
    if variable_start_string is not None:
        env_kwargs["variable_start_string"] = variable_start_string
    if variable_end_string is not None:
        env_kwargs["variable_end_string"] = variable_end_string
    if block_start_string is not None:
        env_kwargs["block_start_string"] = block_start_string
    if block_end_string is not None:
        env_kwargs["block_end_string"] = block_end_string
    if comment_start_string is not None:
        env_kwargs["comment_start_string"] = comment_start_string
    if comment_end_string is not None:
        env_kwargs["comment_end_string"] = comment_end_string
    if line_statement_prefix is not None:
        env_kwargs["line_statement_prefix"] = line_statement_prefix
    if line_comment_prefix is not None:
        env_kwargs["line_comment_prefix"] = line_comment_prefix
    if newline_sequence is not None:
        env_kwargs["newline_sequence"] = newline_sequence

    env = Environment(**env_kwargs)
    if strict:
        env.undefined = StrictUndefined

    # Add environ global
    def _environ(key: str):
        value = os.environ.get(key)
        if value is None and strict:
            raise UndefinedError(f"environment variable '{key}' is not defined")
        return value

    env.globals["environ"] = _environ
    env.globals["get_context"] = lambda: data

    return env.get_template(os.path.basename(template_path)).render(data)


def split_extension_path(extension: str) -> tuple[str, str | None]:
    if ":" in extension:
        module_name, object_name = extension.split(":", 1)
        return module_name, object_name or None
    module_name, _, object_name = extension.rpartition(".")
    if module_name:
        return module_name, object_name or None
    return extension, None


def load_local_module(module_name: str, base_dir: str) -> ModuleType | None:
    module_path = os.path.join(base_dir, *module_name.split("."))
    for candidate in (f"{module_path}.py", os.path.join(module_path, "__init__.py")):
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


def resolve_extension(extension: ExtensionSpec, base_dir: str) -> ExtensionSpec:
    if not isinstance(extension, str):
        return extension
    if extension.startswith("jinja2.ext."):
        return extension
    module_name, object_name = split_extension_path(extension)
    if object_name:
        if importlib.util.find_spec(module_name) is not None:
            module = importlib.import_module(module_name)
        else:
            module = load_local_module(module_name, base_dir)
        if module is None:
            raise ModuleNotFoundError(f"Cannot import {module_name!r}")
        try:
            return getattr(module, object_name)
        except AttributeError as exc:
            raise ModuleNotFoundError(
                f"Cannot import {object_name!r} from {module_name!r}"
            ) from exc
    if importlib.util.find_spec(module_name) is not None:
        return extension
    module = load_local_module(module_name, base_dir)
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
                raise InvalidDataFormat(f"{format}: install pyyaml to fix")
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
            raise raise_exc(f"{data[:60]} ...")
    else:
        data = {}

    extensions = []
    for ext in opts.extensions:
        # Allow shorthand and assume if it's not a module
        # path, it's probably trying to use builtin from jinja2
        if "." not in ext and ":" not in ext:
            ext = f"jinja2.ext.{ext}"
        extensions.append(resolve_extension(ext, os.getcwd()))

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

    out.write(
        render(
            template_path,
            data,
            extensions,
            opts.strict,
            trim_blocks=opts.trim_blocks,
            lstrip_blocks=opts.lstrip_blocks,
            autoescape=opts.autoescape,
            variable_start_string=opts.variable_start,
            variable_end_string=opts.variable_end,
            block_start_string=opts.block_start,
            block_end_string=opts.block_end,
            comment_start_string=opts.comment_start,
            comment_end_string=opts.comment_end,
            line_statement_prefix=opts.line_statement_prefix,
            line_comment_prefix=opts.line_comment_prefix,
            newline_sequence=opts.newline_sequence,
            search_paths=opts.search_paths,
        )
    )
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


class ArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        help_text = help_text.replace(
            FORMAT_HELP_SENTINEL,
            "format of input variables: " + ", ".join(sorted(list(get_available_formats()))),
        )
        return help_text


class VersionAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        from jinja2 import __version__ as jinja_version

        from jinja2cli import __version__

        parser.exit(message=f"jinja2-cli v{__version__}\n - Jinja2 v{jinja_version}\n")


def main() -> None:
    parser = ArgumentParser(usage="%(prog)s [options] <input template> <input data>")
    parser.add_argument(
        "--version",
        action=VersionAction,
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
        "-I",
        "--include",
        help="Add directory to template search path",
        dest="search_paths",
        action="append",
        default=[],
        metavar="DIR",
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
    parser.add_argument(
        "--trim-blocks",
        help="Trim first newline after a block",
        dest="trim_blocks",
        action="store_true",
    )
    parser.add_argument(
        "--lstrip-blocks",
        help="Strip leading spaces and tabs from block start",
        dest="lstrip_blocks",
        action="store_true",
    )
    parser.add_argument(
        "--autoescape",
        help="Enable autoescape",
        dest="autoescape",
        action="store_true",
    )
    parser.add_argument(
        "--variable-start",
        help="Variable start string",
        dest="variable_start",
    )
    parser.add_argument(
        "--variable-end",
        help="Variable end string",
        dest="variable_end",
    )
    parser.add_argument(
        "--block-start",
        help="Block start string",
        dest="block_start",
    )
    parser.add_argument(
        "--block-end",
        help="Block end string",
        dest="block_end",
    )
    parser.add_argument(
        "--comment-start",
        help="Comment start string",
        dest="comment_start",
    )
    parser.add_argument(
        "--comment-end",
        help="Comment end string",
        dest="comment_end",
    )
    parser.add_argument(
        "--line-statement-prefix",
        help="Line statement prefix",
        dest="line_statement_prefix",
    )
    parser.add_argument(
        "--line-comment-prefix",
        help="Line comment prefix",
        dest="line_comment_prefix",
    )
    parser.add_argument(
        "--newline-sequence",
        help=r'Newline sequence (e.g., "\n" or "\r\n")',
        dest="newline_sequence",
    )
    parser.add_argument("template", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("data", nargs="?", help=argparse.SUPPRESS)
    opts = parser.parse_args()
    args = [value for value in (opts.template, opts.data) if value is not None]

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
