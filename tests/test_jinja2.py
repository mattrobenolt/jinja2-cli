import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pytest
import schema

from jinja2cli import __version__ as jinja2cli_version
from jinja2cli import cli
from tests.utils import Data, DataSerializer

from .common import (
    TEMPLATES_FILES_PATH,
    CustomTemplate,
    EnvDataFile,
    HJsonDataFile,
    IniDataFile,
    Json5DataFile,
    JsonDataFile,
    MinData,
    MinDataFile,
    MultiSectionData,
    MultiSectionTemplate,
    QueryStringDataFile,
    SingleSectionData,
    SingleSectionTemplate,
    TomlDataFile,
    TruncatedData,
    TruncatedDataFile,
    XMLData,
    XMLDataFile,
    XMLTemplate,
    YAMLDataFile,
)

# errors ---------------------------------------------------------------------
TemplateNotFoundError = "jinja2.exceptions.TemplateNotFound"
UndefinedDataError = "jinja2.exceptions.UndefinedError: '%s' is undefined"
InvalidFormatError = "jinja2cli.cli.InvalidDataFormat: %s"
SectionError = "ERROR: unknown section. Exiting."


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def run_jinja2(*args, **kwargs):
    """Run jinja2 in a subprocess, sends optional input on stdin and captures
    its output and error streams.

    Arguments are passed with the same order as command line arguments to
    jinja2.

    :param args: a list of strings used as command line arguments for jinja2
    client.
    :type args: list
    :param kwargs: additional arguments for jinja2
    :type kwargs: dict
    :kwargs data: data passed to jinja2 on its stdin
    :type data: str
    :return: a tuple of the error and output streams contents
    :rtype: tuple
    """
    command = ["jinja2"] + [arg for arg in args]
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    inp = kwargs.get("data", None)
    if inp:
        if cli.PY3:
            out, err = proc.communicate(bytes(inp, "ascii"))
        else:
            out, err = proc.communicate(inp)
    else:
        out, err = proc.communicate()

    try:
        proc.kill()
    except OSError:
        pass

    return cli.force_text(out), cli.force_text(err)


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------


class TestFiles:
    """Test data files and templates used for testing jinja2cli"""

    @pytest.mark.parametrize(
        ("data"),
        [SingleSectionData, MultiSectionData, XMLData, MinData, TruncatedData],
        ids=str,
    )
    def test_context_data(self, data):
        """Test that templates' context data are valid.

        Steps:
            - assert that template context data is valid.
        Expect:
            - template context data is valid.

        :param data: data used as template context data.
        :type data: an instance of `utils.Data` class.
        """
        try:
            data.validated_data()
        except schema.SchemaError:
            pytest.fail("Data %s is not valid!" % (data))

    @pytest.mark.parametrize(
        ("datafile"),
        [
            EnvDataFile,
            pytest.param(
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            QueryStringDataFile,
            JsonDataFile,
            Json5DataFile,
            pytest.param(
                HJsonDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major < 3), reason="Requires Python3"
                ),
            ),
            YAMLDataFile,
            TomlDataFile,
            XMLDataFile,
            MinDataFile,
            TruncatedDataFile,
        ],
        ids=str,
    )
    def test_datafiles(self, datafile):
        """Check data files exist, and their content is correct.

        Steps:
            - assert that data file exists.
            - assert that data file contents, when loaded and
            parsed, are valid.
        Expect:
            - data file exists.
            - data file content is valid.

        :param datafile: data file that contains context data
        in a specific format.
        :type: an instance of `utils.DataFile` class.
        """
        assert datafile.check_file()
        assert datafile.validate_file()

    @pytest.mark.parametrize(
        ("template"),
        [
            SingleSectionTemplate,
            MultiSectionTemplate,
            XMLTemplate,
        ],
        ids=str,
    )
    def test_templates(self, template):
        """Check template files exist, their content and their
        rendering are correct.

        - Steps:
            - assert that template file exists.
            - assert that template file contents are valid, and
            that the rendered template is valid.
        - Expect:
            - template file exists.
            - template renders correctly.

        :param template: template file used for testing jinja2
        client.
        :type template: an instance of `utils.Template` class
        """
        assert template.check_template_file()
        assert template.validate_template_file()


class TestHelp:
    USAGE = "Usage: jinja2 [options] <input template> <input data>"

    def test_help_short(self):
        """Test that `-h` option shows help message.

        Steps:
            - run jinja2 with '-h' option.
        Expect:
            - jinja2 usage message in stdout.
            - no output on stderr.
        """
        out, err = run_jinja2("-h")
        assert self.USAGE in out
        assert "" == err

    def test_help_long(self):
        """Tets that `--help` option shows help message.

        Steps:
            - run jinja2 with '--help' option.
        Expect:
            - jinja2 usage message in stdout.
            - no output on stderr.
        """
        out, err = run_jinja2("--help")
        assert self.USAGE in out
        assert "" == err

    def test_help_with_other_options(self):
        """Test help option overrides other options

        Steps:
            - run jinja2 with `--help`, `--format` option,
            data file and template arguments.
        Expect:
            - jinja2 usage message in stdout
            - no output o stderr
        """
        out, err = run_jinja2(
            "--help",
            "--format",
            "json",
            SingleSectionTemplate.file,
            JsonDataFile.file,
        )
        assert self.USAGE in out
        assert "" == err


class TestVersion:
    def test_version(self):
        """Test that `--version` displays jinja2cli version

        - Steps:
            - run jinja2 with `--version` options.
        - Expect:
            - jinja2-cli version is in stdout.
            - no output on stderr.
        """
        out, err = run_jinja2("--version")
        assert jinja2cli_version in out
        assert "" == err


class TestJinjaArguments:
    """Test jinja2cli positional arguments"""

    TOO_MANY_ARGS_ERR = "ValueError: too many values to unpack"

    @pytest.mark.xfail
    def test_no_args(self):
        """Test that running jinja2 with no arguments shows
        help message on stderr.

        Steps:
            - run jinja2 without arguments.
        Expect:
            - no output on stdout.
            - help message on stderr.
        """
        out, err = run_jinja2()
        assert "" == out
        assert TestHelp.USAGE in err

    def test_non_exiting_template(self):
        """Test that running jinja2 with an invalid template path
        shows TemplateNotFoundError on stderr.

        Steps:
            - run jinja2 with a path to an data file, and
            a path to non existing template.
        Expect:
            - no output on stdout.
            - template not found error on stderr.
        """
        out, err = run_jinja2(
            "--format",
            "json",
            os.path.join(TEMPLATES_FILES_PATH, "non_existing_template.j2"),
            JsonDataFile.file,
        )
        assert "" == out
        assert TemplateNotFoundError in err

    def test_template_path_and_no_data(self):
        """Test that running jinja2 with template path only,
        renders the template using undefined variables.

        Steps:
            - run jinja2 with path to a template file.
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        rendered = SingleSectionTemplate.render(context={})
        out, err = run_jinja2(SingleSectionTemplate.file)
        assert rendered == out
        assert "" == err

    def test_template_path_and_no_data_error(self):
        """Test that running jinja2 with template path only,
        shows UndefinedDataError on stderr, and doesn't
        render the template when the template requires
        nested data in its context eg: ``{{ foo.bar }}`.

        Steps:
            - run jinja2 with path to a template file.
        Expect:
            - no output on stdout.
            - UndefinedDataError on stdin.
        """
        data = MultiSectionTemplate.data.validated_data()
        undefined_errors = [UndefinedDataError % (k) for k in data.keys()]
        out, err = run_jinja2(MultiSectionTemplate.file)

        for error in undefined_errors:
            if error in err:
                break

        assert "" == out
        assert error in err

    @pytest.mark.parametrize(
        ("template", "datafile"),
        [
            (SingleSectionTemplate, EnvDataFile),
            pytest.param(
                MultiSectionTemplate,
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            (MultiSectionTemplate, QueryStringDataFile),
            (MultiSectionTemplate, JsonDataFile),
            (MultiSectionTemplate, Json5DataFile),
            pytest.param(
                MultiSectionTemplate,
                HJsonDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major < 3), reason="Requires Python3"
                ),
            ),
            (MultiSectionTemplate, TomlDataFile),
            (MultiSectionTemplate, YAMLDataFile),
            (XMLTemplate, XMLDataFile),
        ],
        ids=str,
    )
    def test_template_and_data_implicit_format(self, template, datafile):
        """Test that running jinja2 can guess the data file format from its
        the data file's extension.

        - Steps:
            - run jinja2 with path to the template file,
            and the path to the data file.
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        out, err = run_jinja2(
            template.file,
            datafile.file,
        )
        assert template.render() == out
        assert "" == err

    def test_extra_arguments(self):
        """Test that running jinja2 with too many positional arguments,
        shows too many arguments error on stderr.

        Steps:
            - run jinja2 with path to template file,
            path to data file, and `extra_argument`.
        Expect:
            - no ouput on stdout.
            - TooManyArguments error on stderr.
        """
        out, err = run_jinja2(
            SingleSectionTemplate.file, EnvDataFile.file, "extra_argument"
        )
        assert "" == out
        assert self.TOO_MANY_ARGS_ERR in err


class TestJinjaOptions:
    def write(self, data):
        data = str(data)
        self.buffer = data
        return len(data)

    @pytest.mark.parametrize(
        ("template", "datafile"),
        [
            (SingleSectionTemplate, EnvDataFile),
            pytest.param(
                MultiSectionTemplate,
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            (MultiSectionTemplate, QueryStringDataFile),
            (MultiSectionTemplate, JsonDataFile),
            (MultiSectionTemplate, Json5DataFile),
            pytest.param(
                MultiSectionTemplate,
                HJsonDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major < 3), reason="Requires Python3"
                ),
            ),
            (MultiSectionTemplate, TomlDataFile),
            (MultiSectionTemplate, YAMLDataFile),
            (XMLTemplate, XMLDataFile),
        ],
        ids=str,
    )
    def test_formats_short(self, template, datafile):
        """test that jinja2 accepts short format option `-f`.

        Steps:
            - run jinja2 with short format option '-f',
            data file format, path to template file, and
            path to data file,
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        out, err = run_jinja2(
            "-f", datafile.format, template.file, datafile.file
        )

        assert template.render() == out
        assert "" == err

    @pytest.mark.parametrize(
        ("template", "datafile"),
        [
            (SingleSectionTemplate, EnvDataFile),
            pytest.param(
                MultiSectionTemplate,
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            (MultiSectionTemplate, QueryStringDataFile),
            (MultiSectionTemplate, JsonDataFile),
        ],
        ids=str,
    )
    def test_formats_long(self, template, datafile):
        """test that jinja2 accepts long format option `--format`.

        Steps:
            - run jinja2 with long format option '--format',
            data file format, path to template file, and
            path to data file,
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        out, err = run_jinja2(
            "--format", datafile.format, template.file, datafile.file
        )

        assert template.render() == out
        assert "" == err

    @pytest.mark.parametrize(
        ("template", "datafile"),
        [
            (SingleSectionTemplate, EnvDataFile),
            pytest.param(
                MultiSectionTemplate,
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            (MultiSectionTemplate, QueryStringDataFile),
            (MultiSectionTemplate, JsonDataFile),
            (MultiSectionTemplate, Json5DataFile),
            pytest.param(
                MultiSectionTemplate,
                HJsonDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major < 3), reason="Requires Python3"
                ),
            ),
            (MultiSectionTemplate, TomlDataFile),
            (MultiSectionTemplate, YAMLDataFile),
            (XMLTemplate, XMLDataFile),
        ],
        ids=str,
    )
    def test_format_auto(self, template, datafile):
        """Test that jinja2 renders template files correctly, when
        using `auto` format option.

        Steps:
            - run jinja2 with `auto` as the format option,
            path to template file, and path to data file.
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        out, err = run_jinja2("--format", "auto", template.file, datafile.file)

        assert template.render() == out
        assert "" == err

    def test_unknown_format(self):
        """Test that using an unknown format shows invalid
        format error on stderr.

        Steps:
            - run jinja2 with an unknown format `csv`.
        Expect:
            - no output on stdout.
            - InvalidFormatError in stderr.
        """
        out, err = run_jinja2(
            "--format",
            "csv",
            SingleSectionTemplate.file,
            "-",
            data="foor,bar\nham,spam\n",
        )

        assert "" == out
        assert InvalidFormatError % ("csv") in err

    def test_D_variables(self):
        """Test pasing context data variables using `-D` option

        Steps:
            - run jinja2 with data defined through `-D` option,
            and path to template file.
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        args = list()
        data = SingleSectionTemplate.data.validated_data()
        for k, v in data.items():
            args.append("-D%s=%s" % (k, v))
        args.append(SingleSectionTemplate.file)
        out, err = run_jinja2(*args)

        assert SingleSectionTemplate.render() == out
        assert "" == err

    def test_D_variables_plus_datafile(self):
        """Test that variables defined through `-D` option is
        combined with variables from data file.

        Steps:
            - run jinja2 with a variable defined through `-D` option,
            path to template file and path to data file.
        Expect:
            - template is rendered correctly.
            - no output on stderr.
        """
        diff = {
            k: v
            for (k, v) in SingleSectionTemplate.data.validated_data().items()
            if k not in MinDataFile.data.validated_data()
        }

        args = list()
        for k, v in diff.items():
            args.append("-D%s=%s" % (k, v))

        args.append(SingleSectionTemplate.file)
        args.append(MinDataFile.file)
        out, err = run_jinja2("--format", MinDataFile.format, *args)

        assert SingleSectionTemplate.render() == out
        assert "" == err

    def test_D_variables_overwrite_datafile(self):
        """Test that data defined by `-D` option overwrites
        data from the datafile.

        Steps:
            - run jinja2 with variables defined by `-D` option,
            path to template file, and path to data file.
        Expect:
            - template is rendered using variables defined by
            `-D` option, and is written to stdout.
            - no output on stderr.
        """
        data = JsonDataFile.data.validated_data()
        data["foo"] = "foo"
        data["ham"] = "ham"

        args = ["--format", "json"]
        for k, v in data.items():
            args.append("-D%s=%s" % (k, v))
        args.append(SingleSectionTemplate.file)
        args.append(JsonDataFile.file)
        out, err = run_jinja2(*args)

        assert SingleSectionTemplate.render(data) == out
        assert "" == err

    def test_section_short(self):
        """Test `-s` option discards all data except for
        the defined section.

        Steps:
            - run jinja2 with `--section` option for `extra`,
            path to template file, and `extra_data` piped
            through stdin.
        Expect:
            - template is rendered on stdout using `extra`
            section.
            - no output on stdoerr.
        """
        extra_data = {
            "main": {"foo": "bar", "ham": "spam"},
            "extra": {"foo": "foo", "ham": "ham"},
        }
        out, err = run_jinja2(
            "--format",
            "json",
            "-s",
            "extra",
            SingleSectionTemplate.file,
            "-",
            data=DataSerializer.serialize_data(
                Data(extra_data, schema.Schema(extra_data)), "json"
            ),
        )

        assert SingleSectionTemplate.render(extra_data["extra"]) == out
        assert "" == err

    def test_section_long(self):
        """Test `--section` option discards all data except for
        the defined section.

        Steps:
            - run jinja2 with `--section` option for `extra`,
            path to template file, and `extra_data` piped
            through stdin.
        Expect:
            - template is rendered on stdout using `extra`
            section.
            - no output on stdoerr.
        """
        extra_data = {
            "main": {"foo": "bar", "ham": "spam"},
            "extra": {"foo": "foo", "ham": "ham"},
        }
        out, err = run_jinja2(
            "--format",
            "json",
            "--section",
            "extra",
            SingleSectionTemplate.file,
            "-",
            data=DataSerializer.serialize_data(
                Data(extra_data, schema.Schema(extra_data)), "json"
            ),
        )

        assert SingleSectionTemplate.render(extra_data["extra"]) == out
        assert "" == err

    def test_bad_section(self):
        """Test passing an unknown section name to `--section`
        option shows SectionError on stderr.

        Steps:
            - run jinja2 with `--section` option for `bad_section`,
            templatef file path, and `extra_data` piped through stdin.
        Expect:
            - no output on stdout.
            - SectionError on stderr.
        """
        extra_data = {
            "main": {"foo": "bar", "ham": "spam"},
            "extra": {"foo": "foo", "ham": "ham"},
        }
        out, err = run_jinja2(
            "--format",
            "json",
            "--section",
            "bad_section",
            SingleSectionTemplate.file,
            "-",
            data=DataSerializer.serialize_data(
                Data(extra_data, schema.Schema(extra_data)), "json"
            ),
        )

        assert "" == out
        assert SectionError in err

    def test_missing_data(self):
        """Test jinja2 uses undefined variables to render
        templates, when not using `--strict` option.

        Steps:
            - run jinja2 with path to template file, and
            partial context data piped through stdin.
        Expect:
            - partially rendered template on stdout.
            - no output on stderr.
        """
        missing_data = SingleSectionTemplate.data.validated_data()
        missing_data.pop("ham")
        missing_data = Data(missing_data, schema.Schema(missing_data))
        out, err = run_jinja2(
            "--format",
            "json",
            "--strict",
            SingleSectionTemplate.file,
            "-",
            data=DataSerializer.serialize_data(missing_data, "json"),
        )

        assert out in SingleSectionTemplate.rendered
        assert out != SingleSectionTemplate.rendered
        assert UndefinedDataError % "ham" in err

    def test_strict_missing_data(self):
        """Test `--strict` option prevents jinja2 from using
        undefined variables to render templates.

        Steps:
            - run jinja2 with `--strict` option,
            path to template file, and partial data piped
            through stdin.
        Expect:
            - no output on stdout.
            - undefined data error on stderr.
        """
        missing_data = {"foo": "bar"}
        missing_data = Data(missing_data, schema.Schema(missing_data))
        out, err = run_jinja2(
            "--format",
            "json",
            "--strict",
            SingleSectionTemplate.file,
            "-",
            data=DataSerializer.serialize_data(missing_data, "json"),
        )

        assert "" == out
        assert UndefinedDataError % "ham" in err

    def test_extensions_short(self):
        """Test `-e` option adds extensions to jinja2 environemnt.

        Steps:
            - run jinja2 with `-e` option, path to a template file
            that uses custom tag, and path to data file.
        Expect:
            - template is rendered on stdout.
            - no error on stderr.
        """
        out, err = run_jinja2(
            "-e",
            "utils.UpperCaseExtension",
            "--format",
            "json",
            CustomTemplate.file,
            data=DataSerializer.serialize_data(CustomTemplate.data, "json"),
        )

        assert CustomTemplate.rendered == out
        assert "" == err

    def test_extensions_long(self):
        """Test `--extension` option adds extensions to jinja2
        environemnt.

        Steps:
            - run jinja2 with `--extension` option, path to a
            template file that uses custom tag, and path to data
            file.
        Expect:
            - template is rendered on stdout.
            - no error on stderr.
        """
        out, err = run_jinja2(
            "--extension",
            "utils.UpperCaseExtension",
            "--format",
            "json",
            CustomTemplate.file,
            data=DataSerializer.serialize_data(CustomTemplate.data, "json"),
        )

        assert CustomTemplate.rendered == out
        assert "" == err

    def test_extension_attribute_error(self):
        """Test that adding an unknown relative extension
        shows AttributeError on stderr.

        Steps:
            - run jinja2 with relative import path to an
            unknown extension, path to a custom template
            file, and path to data file.
        Expect:
            - no output on stdout.
            - AttributeError in stderr.
        """
        out, err = run_jinja2(
            "--extension",
            "Foo",
            "--format",
            "json",
            CustomTemplate.file,
            data=DataSerializer.serialize_data(CustomTemplate.data, "json"),
        )

        assert "" == out
        assert "AttributeError" in err

    def test_extension_import_error(self):
        """Test that adding an unknown extension
        shows ImportError on stderr.

        Steps:
            - run jinja2 with import path to an unknown
            extension, path to a custom template file,
            and path to data file.
        Expect:
            - no output on stdout.
            - AttributeError in stderr.
        """
        out, err = run_jinja2(
            "--extension",
            "foo.Bar",
            "--format",
            "json",
            CustomTemplate.file,
            data=DataSerializer.serialize_data(CustomTemplate.data, "json"),
        )

        assert "" == out
        assert "ImportError" in err or "ModuleNotFoundError" in err

    def test_outfile_short(self):
        """Test that `-o` option write rendered template
        to the output file, instead of stdout.

        Steps:
            - run jinja2 with the `-o` option with path to output
            file, path to template file, and path to data file.
            - open the output file and read the rendered template.
        Expect:
            - no output on stdout.
            - no output on stderr.
            - output file contains the rendered temlet.
        """
        outfile = "out.txt"
        out, err = run_jinja2(
            "--format",
            EnvDataFile.format,
            "-o",
            outfile,
            SingleSectionTemplate.file,
            EnvDataFile.file,
        )

        with open(outfile, "r") as f:
            rendered = f.read()

        assert "" == out
        assert "" == err
        assert SingleSectionTemplate.render() == rendered

    def test_outfile_long(self):
        """Test that `--outfile` option write rendered template
        to the output file, instead of stdout.

        Steps:
            - run jinja2 with the `--outfile` option with path to
            output file, path to template file, and path to data file.
            - open the output file and read the rendered template.
        Expect:
            - no output on stdout.
            - no output on stderr.
            - output file contains the rendered temlet.
        """
        outfile = "out.txt"
        out, err = run_jinja2(
            "--format",
            EnvDataFile.format,
            "--outfile",
            outfile,
            SingleSectionTemplate.file,
            EnvDataFile.file,
        )

        with open(outfile, "r") as f:
            rendered = f.read()

        assert "" == out
        assert "" == err
        assert SingleSectionTemplate.render() == rendered


class TestStdin:
    @pytest.mark.parametrize(
        ("template", "datafile"),
        [
            (SingleSectionTemplate, EnvDataFile),
            pytest.param(
                MultiSectionTemplate,
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            (MultiSectionTemplate, QueryStringDataFile),
            (MultiSectionTemplate, JsonDataFile),
            (MultiSectionTemplate, Json5DataFile),
            pytest.param(
                MultiSectionTemplate,
                HJsonDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major < 3), reason="Requires Python3"
                ),
            ),
            (MultiSectionTemplate, TomlDataFile),
            (MultiSectionTemplate, YAMLDataFile),
            (XMLTemplate, XMLDataFile),
        ],
        ids=str,
    )
    def test_data_from_dash_stdin(self, template, datafile):
        """Run jinja2 with template, and data is provided through
        stdin, by adding dash '-' option. Data format is specified by
        the `--format` option.

        Expect:
            - rendered template on stdout
            - no output on stdin

        :param template: template used for the test
        :type template: an instance of Template class
        :param datafile: data file that contains context data
        in a specific format.
        :type: an instance of `utils.DataFile` class.
        """
        data_string = DataSerializer.serialize_data(
            datafile.data, datafile.format
        )
        out, err = run_jinja2(
            "--format", datafile.format, template.file, "-", data=data_string
        )
        assert template.render() == out
        assert "" == err

    @pytest.mark.parametrize(
        ("template", "datafile"),
        [
            (SingleSectionTemplate, EnvDataFile),
            pytest.param(
                MultiSectionTemplate,
                IniDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major, sys.version_info.minor)
                    == (3, 12),
                    reason="Python3.12 removed configparse.readfp()",
                ),
            ),
            (MultiSectionTemplate, QueryStringDataFile),
            (MultiSectionTemplate, JsonDataFile),
            (MultiSectionTemplate, Json5DataFile),
            pytest.param(
                MultiSectionTemplate,
                HJsonDataFile,
                marks=pytest.mark.skipif(
                    (sys.version_info.major < 3), reason="Requires Python3"
                ),
            ),
            (MultiSectionTemplate, TomlDataFile),
            (MultiSectionTemplate, YAMLDataFile),
            (XMLTemplate, XMLDataFile),
        ],
        ids=str,
    )
    def test_data_from_implicit_stdin(self, template, datafile):
        """Run jinja2 with template, and data is provided through
        stdin. Data format is specified by the `--format` option.

        Expect:
            - rendered template on stdout
            - no output on stdin

        :param template: template used for the test
        :type template: an instance of Template class
        :param datafile: data file that contains context data
        in a specific format.
        :type: an instance of `utils.DataFile` class.
        """
        data_string = DataSerializer.serialize_data(
            datafile.data, datafile.format
        )
        out, err = run_jinja2(
            "--format", datafile.format, template.file, data=data_string
        )
        assert template.render() == out
        assert "" == err


class TestEnvFormat:
    @pytest.mark.xfail
    def test_multiline_env(self):
        """Test that jinja2 can parse multiline env variables

        Steps:
            - run jinja2 with '-f' option for env format,
            path to template file, and variable piped through
            stdin.
        Expect:
            - rendered template on stdout.
            - no output on stderr.
        """
        multiline_env_data = "foo=b\na\nr\nham=spam"
        out, err = run_jinja2(
            "-f", "env", SingleSectionTemplate.file, data=multiline_env_data
        )

        assert (
            SingleSectionTemplate.render(
                {
                    "foo": "b\na\nr\n",
                    "ham": "spam",
                }
            )
            == out
        )

        assert "" == err
