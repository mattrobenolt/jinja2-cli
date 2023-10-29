"""utils.py defines helper classes for testing jinja2cli:

    * UpperCaseExtension: A jinja2 extension that adds `uppercase`
      tag, that changes the case of all text within the block to
      upper case.
    * Template: a class that represents a template file, what the
      template file contains, its context data and the expected result
      after the template is rendered.
    * Data: a class that represents template's context data as
      serializable data.
    * DataSerializer: a class that registers data serializers classes
      and provides an API for serializing and deserializng data in
      different formats.
    * BaseSerializer: A base class for serializers, provide a simple
      API for data serialization and deserialization
    * StringSerializer: A subclass of `BaseSerializer`, and a base
      class for serializers that serialize data into strings.
    * EnvSerializer: A subclass of `StringSerializer`, serialize data
      into `env` format:
          `key_1=value_1\nkey_2=value_2\n...`.
    * IniSerializer: A subclass of `StringSerializer`, serialize data
      into `ini` format:
          `[section]\nkey_1=value_1\n[section_2]\nkey_2=value_2...`.
    * QuerystringSerializer: A subclass of `StringSerializer`,
      serialize data into `querystring` format:
          `key_1=value_1&key_2=value_2...`
    * JsonSerializer: A subclass of `StringSerializer`, serilize
      data into `json` format:
          `{"key_1": value_1, "key_2": value_2, ...}`
    * Json5Serializer: A subclass of `StringSerializer`, serializse
      data into `json5` format:
          `{key_1: "value-1", key_2: "value_2", ...}`
    * HJsonSerializer: A subclass of `StringSerializer`, serializse
      data into `hjson` format:
          `
            {
                key_1: value_1,
                key_2: value_2,
                ...
            }
          `
    * YAMLSerializer: A subclass of `StringSerializer`, serializse
      data into `YAML` format:
          `key_1: value_1\nkey_2: value_2\n...`
    * TomlSerializer: A subclass of `StringSerializer`, serializse
      data into `toml` format:
          `key_1 = value_1\nkey_2 = value_2\n...`
    * XMLSerializer: A subclass of `StringSerializer`, serializse
      data into `xml` format:
          `<data><key_1>value_1</key_1>...</data>`
"""
import json
import os

import json5
import toml
import xmltodict
import yaml
from jinja2 import nodes
from jinja2.ext import Extension

from jinja2cli import cli

try:
    import hjson
except ImportError:
    pass


class UpperCaseExtension(Extension):
    """A custom jinja2 extension that adds a new tag `upperrcase`,
    an upper case block capitalizes all text an variables within
    the block.

    example:
        ```template.j2
        ..
        {% uppercase %}{{foo}}{% enduppercase %}
        ..
        ```

        ```
        >>> import jinja2
        >>> from utils import UpperCaseExtension

        >>> env = jinja2.Environment(extensions=[UpperCaseExtension])
        >>> loader = jinja2.FileSystemLoader("path/to/templates/dir")
        >>> template = loader.load(env, "template.j2")
        >>> render = template.render(foo="bar")
        >>> print(render)
        BAR
        ```
    """

    tags = {"uppercase"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = []  # the uppercase tag doesn't require any arguments
        body = parser.parse_statements(["name:enduppercase"], drop_needle=True)
        ret = nodes.CallBlock(
            self.call_method("_uppercase", args), [], [], body
        ).set_lineno(lineno)
        return ret

    def _uppercase(self, caller=None):
        if caller is not None:
            return caller().upper()
        return ""


class Template(object):
    """Test template file

    attributes:
        * template_file: path to the template file
        * template: template String
        * render:ed: rendered template string
        * data: template context data
    """

    def __init__(self, template_file, template, rendered, data):
        self.file = (
            template_file
            if os.path.isabs(template_file)
            else os.path.abspath(template_file)
        )
        self.template = template
        self.rendered = rendered
        self.data = data

    def make_template_file(self):
        """create template file"""
        with open(self.file, "w") as df:
            df.write(self.template)

    def validate_template_file(self):
        """check that the template file content is corrent

        :return: True if the template file contents are the same
        as the template string
        :rtype: bool
        """
        with open(self.file, "r") as df:
            template = df.read()

        return template == self.template and self.rendered == self.render()

    def check_template_file(self):
        """check that the template file exists

        :return: True if the template file exists
        :rtype: bool
        """
        return os.path.isfile(self.file)

    def render(self, context=None, extensions=None, **additional_context):
        """Render the template using its context data, or different
        context data, and return the rendered result as a string.

        Additional context data can be added to eiher overwrite
        context data, or add more variables.

        :param context: a dictionary that contains the context data
        to used for rendering the template. If context is None, the
        context data is retrieved form the tenplate's `.data` property
        :type context: dict
        :param extension: jinja2 extensions used to render the template
        :type extension: list
        :param additional_context: dictionary with additional context
        data to update the context with
        :type additional_context: dict
        :return: the rendered template as a string
        :rtype: str
        """
        context = (
            context if context is not None else self.data.validated_data()
        )
        for k, v in additional_context:
            context[k] = v
        return cli.force_text(cli.render(self.file, context, extensions or []))

    def validate_rendered(self, rendered):
        """check that the rendered template is correct

        :param rendered: rendered template
        :type rendered: str
        :return: True if rendered template is correct
        :rtype: bool
        """
        return self.rendered == rendered

    def __str__(self):
        return "Template(%s)" % (os.path.split(self.file)[-1])


class Data(object):
    """Serializable data class used to test jinja2cli"""

    def __init__(self, data, schema):
        self.data = data
        self.serial_data = None
        self.schema = schema

    def validated_data(self):
        """return data validated by the validation schema

        :raises: schema.SchemaError if the data is not valid
        :return: data
        :rtype: Any
        """
        return self.schema.validate(self.data)

    def serialize(self, serializer):
        """serialize current data using given serializer

        After calling, the `serial_data` property contains the serial
        representation of the data.

        :param serializer: serializer used to serializer the data
        :type serializer: an object of a class that implements
        `BaseSerializer`.
        :return: serial representation of the data
        :rtype: string
        """
        self.serial_data = serializer.serialize_data(self.data)
        return self.serial_data

    def deserialize(self, serializer):
        """
        deserialize current serial data into a python opject that
        represents the serial data.

        After calling, the `data` property contains a dictionary,
        that represents the serial data.

        :param serializer: serializer that is used to deserialize
        the serial_data into its python representation.
        :type serializer: an object of a class that implements
        `BaseSerializer`.
        :return: a deserialized representation of the data
        :rtype: dict
        """
        self.data = serializer.deserialize_data(self.serial_data)
        return self.data

    def __str__(self):
        return str(self.serial_data) if self.serial_data else str(self.data)


class DataSerializer(object):
    """A class for registering serializer classes, and
    serializing/deserializing `Data` objects, using registred
    serializers.
    Each serializer class is mapped to a unique format so that
    it can be retrieved using that format.
    """

    _serializer_classes = {}

    @classmethod
    def register_serializer(cls, format, serializer_class):
        """Register the serializer class for a format.

        `format` must be unique for each serializer class, using
        the same format to register more than 1 serializer class
        will result in an overwrite.

        :param format: format to map the serializer class to.
        :type format: str
        :param serializer_class: serializer class to register
        :type serializer_class: a subclass of `StringSerializer`
        """
        cls._serializer_classes[format] = serializer_class

    @classmethod
    def get_serializer_class(cls, format):
        """Get serializer class associated with a format.

        Format must be registred with a serializer class using
        `.register_serializer_class()` method.

        :raises NotImplementedError: if `format` is not registered
        with a serializer class.

        :param format: format to get its serializer class
        :type format: str
        :return: a subclass of `StringSerializer`
        """
        try:
            serializer_class = cls._serializer_classes[format]
        except KeyError:
            raise NotImplementedError(
                "Format %s is not implemented." % (format)
            )
        return serializer_class

    @classmethod
    def serialize_data(cls, serializable, format):
        """Serialize given serializable data using the serializer
        class associated with `format`.

        :param serializable: serializable data
        :type serializable: an instance of `Data` subclass.
        :param format: format to use for data serialization.
        :type format: str
        :return: serial representation of the data.
        :rtype: Any
        """
        serializer_class = cls.get_serializer_class(format)
        return serializable.serialize(serializer_class())

    @classmethod
    def deserialize_data(cls, serializable, format):
        """Deserialize given serial representation of a serializable
        data, using the serializer class associated with `fromat`.

        :param serializable: serialized data
        :type serializable: an instance of `Data` subclass.
        :param format: format to use for data serialization.
        :type format: str
        :return: python object that represents the serial data.
        :rtype: Any
        """

        serializer_class = cls.get_serializer_class(format)
        return serializable.deserialize(serializer_class())


class BaseSerializer(object):
    """Base calss that defines a generic interface for serializers.
    A serializer subclass must implement at least one of
    `serializer_data` and `deserialize_data` methods.
    """

    def serialize_data(self, data):
        """translate serializable python object into a serial
        representation.

        :param data: data to be serialized.
        :type data: an instance of `Data` subclass.
        :return: serialized representation of the data.
        :rtype: Any
        :return: data in a serial representation.
        :rtype: Any
        """
        raise NotImplementedError("serialize_data mrthod is not implemented")

    def deserialize_data(self, serial_data):
        """Deserialize serial data into a python object.

        `serial_data` must be in the correct format for the serializer.
        The returned python object is usually a dictionary, but can
        differ depending on the serializer.

        :param serial_data: serial representation of the data.
        :type serial_data: Any
        :return: python object that represents the data as a python
        object.
        :rtype: Any
        """
        raise NotImplementedError("deserialize_data method is not implemented")


class StringSerializer(BaseSerializer):
    """A base class for string serializers, that translate serializable
    python objects to strings, and vice versa.
    """

    def _deserialize_data(self, serial_data, fmt):
        """A private method that uses `jinja2cli.cli.format`
        to deserialize string data, depending on their format.

        :param serial_data: serial data
        :type serial_data: Any
        :param fmt: format of the serial data
        :type fmt: str
        :return: a python object that represents the serial data
        :rtype: Any
        :raises NotImplementedError when `fmt` is not registered
        in `DataSerializer` with a serializer class.
        """
        try:
            fn, except_exc, raise_exc = cli.get_format(fmt)
        except KeyError:
            raise NotImplementedError("Format %s is not supported" % (fmt))

        try:
            data = fn(serial_data)
        except except_exc:
            raise raise_exc("%s..." % (serial_data[:60]))

        return data or {}

    def __str__(self):
        return "StringSerializer"


class EnvSerializer(StringSerializer):
    def __init__(self):
        self._last_key = None

    def serialize_data(self, data):
        serial_data = ""
        for k, v in data.items():
            serial_data += "%s=%s\n" % (k, v)
        return serial_data

    def deserialize_data(self, serial_data):
        return super(EnvSerializer, self)._deserialize_data(serial_data, "env")

    def __str__(self):
        return "EnvSerializer"


class IniSerializer(StringSerializer):
    def serialize_data(self, data):
        serial_data = ""
        for k, v in data.items():
            if isinstance(v, dict):
                serial_data += "[%s]\n" % (k)
                serial_data += self.serialize_data(v)
            else:
                serial_data += "%s=%s\n" % (k, v)
        return serial_data

    def deserialize_data(self, serial_data):
        return super(IniSerializer, self)._deserialize_data(serial_data, "ini")

    def __str__(self):
        return "IniSerializer"


class QuerystringSerializer(StringSerializer):
    def _make_querystring(self, data, prefix=None):
        serial_data = list()
        for k, v in data.items():
            if prefix is not None:
                k = "%s.%s" % (prefix, k)
            if isinstance(v, dict):
                serial_data.extend(self._make_querystring(v, prefix=k))
            else:
                serial_data.append("%s=%s" % (k, v))
        return serial_data

    def serialize_data(self, data):
        return "&".join(self._make_querystring(data))

    def deserialize_data(self, serial_data):
        return super(QuerystringSerializer, self)._deserialize_data(
            serial_data, "querystring"
        )

    def __str__(self):
        return "QuerystringSerializer"


class JsonSerializer(StringSerializer):
    def serialize_data(self, data):
        return cli.force_text(json.dumps(data))

    def deserialize_data(self, serial_data):
        return super(JsonSerializer, self)._deserialize_data(
            serial_data, "json"
        )

    def __str__(self):
        return "JsonSerializer"


class HJsonSerializer(StringSerializer):
    def serialize_data(self, data):
        try:
            serial_data = cli.force_text(hjson.dumps(data))
        except NameError as name_err:
            raise name_err
        finally:
            return serial_data

    def deserialize_data(self, serial_data):
        return super(HJsonSerializer, self)._deserialize_data(
            serial_data, "hjson"
        )

    def __str__(self):
        return "HJsonSerializer"


class Json5Serializer(StringSerializer):
    def serialize_data(self, data):
        return cli.force_text(json5.dumps(data))

    def deserialize_data(self, serial_data):
        return super(Json5Serializer, self)._deserialize_data(
            serial_data, "json5"
        )

    def __str__(self):
        return "Json5Serializer"


class YAMLSerializer(StringSerializer):
    def serialize_data(self, data):
        return cli.force_text(yaml.dump(data, Dumper=yaml.SafeDumper))

    def deserialize_data(self, serial_data):
        return super(YAMLSerializer, self)._deserialize_data(
            serial_data, "yaml"
        )

    def __str__(self):
        return "YAMLSerializer"


class TomlSerializer(StringSerializer):
    def serialize_data(self, data):
        return cli.force_text(toml.dumps(data))

    def deserialize_data(self, serial_data):
        return super(TomlSerializer, self)._deserialize_data(
            serial_data, "toml"
        )

    def __str__(self):
        return "TomlSerializer"


class XMLSerializer(StringSerializer):
    def serialize_data(self, data):
        return cli.force_text(xmltodict.unparse(data))

    def deserialize_data(self, serial_data):
        return super(XMLSerializer, self)._deserialize_data(serial_data, "xml")

    def __str__(self):
        return "XMLSerializer"


class DataFile(object):
    """Class for reading, writing and validating test data files.

    attributes:
        * file: path of the data file.
        * format: file's data format.
        * data: exected data in the file.
    """

    def __init__(self, filepath, format, data):
        self.file = (
            os.path.abspath(filepath)
            if not os.path.isabs(filepath)
            else filepath
        )
        self.format = format
        self.data = data

    def check_file(self):
        """Check that the data file exists.

        :return: True if the file path exists, and points to a file.
        :rtype: bool
        """
        return os.path.isfile(self.file)

    def validate_file(self):
        """Validates the data file's content.

        :return: data read from the file
        :rtype: Any
        """
        if not self.check_file():
            return False
        file_data = Data(self.read_file(), self.data.schema)
        return file_data.validated_data()

    def write_file(self):
        """Serialize file data and write them to the file.

        :return: serial data written to the file
        :rtype: str
        """
        serial_data = DataSerializer.serialize_data(self.data, self.format)
        with open(self.file, "w") as df:
            df.write(serial_data)
        return serial_data

    def read_file(self):
        """Read data from the file and deserialize it.

        :return: deserialized data
        :rtype: Any
        """
        with open(self.file, "r") as df:
            file_data = df.read()
        data = Data(None, self.data.schema)
        data.serial_data = file_data
        return DataSerializer.deserialize_data(data, self.format)

    def __str__(self):
        return "DataFile(%s)" % (os.path.split(self.file)[-1])


# if __name__ == "__main__":
#
#     class XMLSerializer(StringSerializer):
#         def serialize_data(self, data):
#             from xmltodict import unparse
#
#             return xmltodict.unparse(data)
#
#         def deserialize_data(self, serial_data):
#             from xmltodict import parse
#
#             return parse(serial_data)
#
#     single_section_data = {"foo": "bar", "ham": "spam"}
#     multi_section_data = {
#         "section_1": {
#             "foo": "bar",
#         },
#         "section_2": {"ham": "spam"},
#     }
#     xml_data = {"data": {"foo": "bar", "ham": "spam"}}
#
#     SingleSectionDataSchema = schema.Schema(single_section_data)
#     MultiSectionDataSchema = schema.Schema(multi_section_data)
#     XMLDataSchema = schema.Schema(xml_data)
#
#     SingleSectionData = Data(single_section_data, SingleSectionDataSchema)
#     MultiSectionData = Data(multi_section_data, MultiSectionDataSchema)
#     XMLData = Data(xml_data, XMLDataSchema)
#
#     xml_file_path = os.path.join(os.path.dirname(__file__), "files", "data", "data.xml")
#     XMLDataFile = DataFile(xml_file_path, "xml", XMLData)
#
#     DataSerializer.register_serializer("xml", XMLSerializer)
#
#     assert XMLDataFile.check_file()
#     assert XMLDataFile.read_file()
#     assert XMLDataFile.validate_file()
