# $ jinja2
A CLI interface to Jinja2
```
$ jinja2 helloworld.tmpl data.json --format=json
$ cat data.json | jinja2 helloworld.tmpl
$ curl -s http://httpbin.org/ip | jinja2 helloip.tmpl
$ curl -s http://httpbin.org/ip | jinja2 helloip.tmpl > helloip.html
```

## Install
`$ pip install jinja2-cli`

## Usage
```
Usage: jinja2 [options] <input template> <input data>

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --format=FORMAT       format of input variables: auto, ini, json,
                        querystring, yaml, yml
  -e EXTENSIONS, --extension=EXTENSIONS
                        extra jinja2 extensions to load
  -D key=value          Define template variable in the form of key=value
  -s SECTION, --section=SECTION
                        Use only this section from the configuration
  --strict              Disallow undefined variables to be used within the
                        template
  --latex               Use markers that are compatible with LaTeX
```

## Optional YAML support
If `PyYAML` is present, you can use YAML as an input data source.

`$ pip install jinja2-cli[yaml]`

## Optional TOML support
If `toml` is present, you can use TOML as an input data source.

`$ pip install jinja2-cli[toml]`

## Optional XML support
If `xmltodict` is present, you can use XML as an input data source.

`$ pip install jinja2-cli[xml]`

## LaTeX support
The default markers used by Jinja2 are incompatible with LaTeX, as explained
in blog posts by [Brad Erickson] and [Arthur Miller]. The option `--latex`
changes the default markers to the following ones by passing , which are compatible with
LaTeX and do not require any special escaping.

| Default markers       | LaTeX mode        | Jinja2 env settings     |
| :-------------------- | :---------------- | :---------------------- |
| `{%` ... `%}`         | `\BLOCK{` ... `}` | `block_*_string`        |
| `{{` ... `}}`         |  `\VAR{`... `}`   | `variable_*_string`     |
| `{#` ... `#}`         |  `\#{` ... `}`    | `comment_*_string`      |
|	*disabled by default* | `%%`              | `line_statement_prefix` |
|	*disabled by default* | `%#`              | `line_comment_prefix`   |

In addition, the option `trim_blocks` is set to true, and `autoescape` set to
false.

Example usage:
```
jinja2 --latex samples/sample.tex samples/sample.json
```

[Brad Erickson]: http://eosrei.net/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs
[Arthur Miller]: https://miller-blog.com/latex-with-jinja2/
## TODO
 * Variable inheritance and overrides
  * Tests!
