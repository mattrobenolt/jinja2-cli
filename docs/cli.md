# CLI reference

```
usage: jinja2 [options] <input template> <input data>

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -f, --format FORMAT   format of input variables: auto, env, hjson, ini, json, json5, querystring, toml, xml, yaml, yml
  -e, --extension EXTENSIONS
                        extra jinja2 extensions to load
  -D key=value          Define template variable in the form of key=value
  -I, --include DIR     Add directory to template search path
  -s, --section SECTION
                        Use only this section from the configuration
  --strict              Disallow undefined variables to be used within the template
  -o, --outfile FILE    File to use for output. Default is stdout.
  --trim-blocks         Trim first newline after a block
  --lstrip-blocks       Strip leading spaces and tabs from block start
  --autoescape          Enable autoescape
  --variable-start VARIABLE_START
                        Variable start string
  --variable-end VARIABLE_END
                        Variable end string
  --block-start BLOCK_START
                        Block start string
  --block-end BLOCK_END
                        Block end string
  --comment-start COMMENT_START
                        Comment start string
  --comment-end COMMENT_END
                        Comment end string
  --line-statement-prefix LINE_STATEMENT_PREFIX
                        Line statement prefix
  --line-comment-prefix LINE_COMMENT_PREFIX
                        Line comment prefix
  --newline-sequence NEWLINE_SEQUENCE
                        Newline sequence (e.g., "\n" or "\r\n")
  -S, --stream          Read template from stdin (no template file argument)
```

## Notes
- If input data is omitted (or `-`) and stdin is not a TTY, data is read from
  stdin.
- Use `--section` to select a top-level key from the input data.
- Use `-I` to add directories to the template search path. This allows templates
  to include/import from those directories. Can be specified multiple times.
- Use `-S/--stream` to read the template from stdin. In this mode, no template
  file is expected; use `-D` to pass variables.

## Template globals

### `environ(key)`
Access environment variables:
```jinja
{{ environ("HOME") }}
{{ environ("USER") }}
```

Returns `None` if the variable is not set. With `--strict`, raises an error
for missing variables.

### `get_context()`
Access the root data context. Useful for iterating over all input data:
```jinja
{{ get_context() | length }} entries

{% for key, value in get_context().items() %}
{{ key }}: {{ value }}
{% endfor %}
```
