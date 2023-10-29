"""common.py provides common configurations & variables for testing jinja2cli:

configuration variables:
    * paths used for templates and data files:
        - TEST_FILES_PATH: base directory for test files `jinja2cli/tests/files/`
        - DATA_FILES_PATH: base directory for data files `jinja2cli/tests/files/data`
    * content of different templates:
        - SINGLE_SECTION_TEMPLATE
        - MULTI_SECTION_TEMPLATE
        - XML_TEMPLATE
    * expected rendered templates:
        - SINGLE_SECTION_RENDERED_TEMPLATE
        - MULTI_SECTION_RENDERED_TEMPLATE
        - XML_RENDERED_TEMPLATE

variables:
    * Data used for templates context data:
        - _SingleSectionData
        - _MultiSectionData
        - _XMLData
        - _MinData
        - _TruncatedData
    * Data files that contains variables for templates context data:
        - EnvDataFile
        - IniDataFile
        - QueryStringDataFile
        - JsonDataFile
        - Json5DataFile
        - HJsonDataFile
        - TomlDataFile
        - YAMLDataFile
        - XMLDataFile
    * Templates that poiny to tenplate files, their content, expected result
      and context data:
        - SingleSectionTemplate
        - MultiSectionTemplate
        - XMLTemplate
        - CustomTemplate

Serializer registeration, only serializers that use built-in python
packages are registered by this module:
    - "env": EnvSerializer
    - "ini": IniSerializer
    - "querystring": QuerystringSerializer
    - "json": JsonSerializer
    - "json5": Json5Serializer
    - "hjson": HJsonSerializer
    - "toml": TomlSerializer
    - "yaml": YAMLSerializer
    - "xml": XMLSerializer
"""
import os

import schema

from .utils import (
    Data,
    DataFile,
    DataSerializer,
    EnvSerializer,
    HJsonSerializer,
    IniSerializer,
    Json5Serializer,
    JsonSerializer,
    QuerystringSerializer,
    Template,
    TomlSerializer,
    XMLSerializer,
    YAMLSerializer,
)

# Paths ----------------------------------------------------------------------
TEST_FILES_PATH = os.path.join(os.path.dirname(__file__), "files")
DATA_FILES_PATH = os.path.join(TEST_FILES_PATH, "data")
TEMPLATES_FILES_PATH = TEST_FILES_PATH

# Data -----------------------------------------------------------------------
_SingleSectionDataData = {"foo": "bar", "ham": "spam"}
_MultiSectionDataData = {
    "section_1": {"foo": "bar"},
    "section_2": {"ham": "spam"},
}

_XMLDataData = {"data": {"foo": "bar", "ham": "spam"}}
_MinData = {"foo": "bar"}
_TruncatedData = {"section_1": {"foo": "bar"}}

SingleSectionData = Data(
    _SingleSectionDataData, schema.Schema(_SingleSectionDataData)
)
MultiSectionData = Data(
    _MultiSectionDataData, schema.Schema(_MultiSectionDataData)
)
XMLData = Data(_XMLDataData, schema.Schema(_XMLDataData))
MinData = Data(_MinData, schema.Schema(_MinData))
TruncatedData = Data(_TruncatedData, schema.Schema(_TruncatedData))

# Templates ------------------------------------------------------------------
SINGLE_SECTION_TEMPLATE = """
## Data

- Foo: {{foo}}
- Ham: {{ham}}
"""

MULTI_SECTION_TEMPLATE = """
## Section 1

- Foo: {{ section_1.foo }}

## Section 2

- Ham: {{ section_2.ham }}
"""

XML_TEMPLATE = """
## Data

- Foo: {{data.foo}}
- Ham: {{data.ham}}
"""

CUSTOM_TEMPLATE = """
## Data

- Foo: {% uppercase %}{{foo}}{% enduppercase %}
- Ham: {{ham}}
"""

# expanded templates ---------------------------------------------------------
SINGLE_SECTION_RENDERED_TEMPLATE = XML_RENDERED_TEMPLATE = """
## Data

- Foo: bar
- Ham: spam
"""

MULTI_SECTION_RENDERED_TEMPLATE = """
## Section 1

- Foo: bar

## Section 2

- Ham: spam
"""

CUSTOM_RENDERED_TEMPLATE = """
## Data

- Foo: BAR
- Ham: spam
"""

SingleSectionTemplate = Template(
    os.path.join(TEMPLATES_FILES_PATH, "single_section_template.j2"),
    SINGLE_SECTION_TEMPLATE,
    SINGLE_SECTION_RENDERED_TEMPLATE,
    SingleSectionData,
)

MultiSectionTemplate = Template(
    os.path.join(TEMPLATES_FILES_PATH, "multi_section_template.j2"),
    MULTI_SECTION_TEMPLATE,
    MULTI_SECTION_RENDERED_TEMPLATE,
    MultiSectionData,
)

XMLTemplate = Template(
    os.path.join(TEMPLATES_FILES_PATH, "xml_template.j2"),
    XML_TEMPLATE,
    XML_RENDERED_TEMPLATE,
    XMLData,
)

CustomTemplate = Template(
    os.path.join(TEMPLATES_FILES_PATH, "custom_template.j2"),
    CUSTOM_TEMPLATE,
    CUSTOM_RENDERED_TEMPLATE,
    SingleSectionData,
)

# Data files -----------------------------------------------------------------
EnvDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.env"), "env", SingleSectionData
)
IniDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.ini"), "ini", MultiSectionData
)
QueryStringDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.querystring"),
    "querystring",
    MultiSectionData,
)
JsonDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.json"), "json", MultiSectionData
)
Json5DataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.json5"), "json5", MultiSectionData
)
HJsonDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.hjson"), "hjson", MultiSectionData
)
YAMLDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.yml"), "yml", MultiSectionData
)
TomlDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.toml"), "toml", MultiSectionData
)
XMLDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "data.xml"), "xml", XMLData
)
MinDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "min_data.json"), "json", MinData
)
TruncatedDataFile = DataFile(
    os.path.join(DATA_FILES_PATH, "trunc_data.json"),
    "json",
    TruncatedData,
)

# Serializers Registration ---------------------------------------------------
DataSerializer.register_serializer("env", EnvSerializer)
DataSerializer.register_serializer("ini", IniSerializer)
DataSerializer.register_serializer("querystring", QuerystringSerializer)
DataSerializer.register_serializer("json", JsonSerializer)
DataSerializer.register_serializer("json5", Json5Serializer)
DataSerializer.register_serializer("hjson", HJsonSerializer)
DataSerializer.register_serializer("yml", YAMLSerializer)
DataSerializer.register_serializer("toml", TomlSerializer)
DataSerializer.register_serializer("xml", XMLSerializer)
