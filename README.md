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
  ```

## Optional YAML support
If PyYAML is present, you can use YAML as an input data source.

`$ pip install pyyaml`

## TODO
 * Variable inheritance and overrides
 * Make environment variables accessible to templates
 * Pass through m4/gcc-like variables: `jinja2 -Dname=matt`
 * Tests!
