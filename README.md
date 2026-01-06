# $ jinja2
A CLI interface to Jinja2
```
$ jinja2 helloworld.tmpl data.json --format=json
$ cat data.json | jinja2 helloworld.tmpl
$ curl -s http://httpbin.org/ip | jinja2 helloip.tmpl
$ curl -s http://httpbin.org/ip | jinja2 helloip.tmpl > helloip.html
```

## Install
```
$ uv tool install jinja2-cli
# or
$ pip install jinja2-cli
```

## Usage
```
usage: jinja2 [options] <input template> <input data>

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -f, --format FORMAT   format of input variables: auto, env, hjson, ini, json, json5, querystring, toml, xml, yaml, yml
  -e, --extension EXTENSIONS
                        extra jinja2 extensions to load
  -D key=value          Define template variable in the form of key=value
  -s, --section SECTION
                        Use only this section from the configuration
  --strict              Disallow undefined variables to be used within the template
  -o, --outfile FILE    File to use for output. Default is stdout.
```

If the input data is omitted (or `-`) and stdin is not a TTY, data is read from
stdin.

## Extensions
Built-in extensions can be passed as short names (e.g., `-e do`). For local
extensions, use `module:ClassName` and keep the module in the working directory:

```
$ jinja2 template.j2 data.json -e myext:MyExtension
```

## Optional YAML support
If `PyYAML` is present, you can use YAML as an input data source.

`$ uv tool install jinja2-cli[yaml]` or `$ pip install jinja2-cli[yaml]`

## Optional TOML support
If `tomli` is present (Python < 3.11), you can use TOML as an input data source.

`$ uv tool install jinja2-cli[toml]` or `$ pip install jinja2-cli[toml]`

## Optional XML support
If `xmltodict` is present, you can use XML as an input data source.

`$ uv tool install jinja2-cli[xml]` or `$ pip install jinja2-cli[xml]`

## Optional HJSON support
If `hjson` is present, you can use HJSON as an input data source.

`$ uv tool install jinja2-cli[hjson]` or `$ pip install jinja2-cli[hjson]`

## Optional JSON5 support
If `json5` is present, you can use JSON5 as an input data source.

`$ uv tool install jinja2-cli[json5]` or `$ pip install jinja2-cli[json5]`
