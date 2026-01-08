# Examples

## Render config in a container entrypoint
A common pattern is to render config files at container startup from env vars
and a template.

`Dockerfile`:
```Dockerfile
COPY nginx.conf.j2 /etc/nginx/nginx.conf.j2
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
```

`docker-entrypoint.sh`:
```sh
#!/usr/bin/env sh
set -e

jinja2 /etc/nginx/nginx.conf.j2 - --format env <<EOF >/etc/nginx/nginx.conf
SERVER_NAME=$SERVER_NAME
UPSTREAM=$UPSTREAM
EOF

exec nginx -g "daemon off;"
```

## Render a file from JSON
```sh
$ jinja2 template.j2 data.json --format json
```

## Render a file from YAML
```sh
$ jinja2 template.j2 data.yaml --format yaml
```

## Render from stdin
```sh
$ cat data.json | jinja2 template.j2 - --format json
```

## Multiple data files
Merge multiple data files together. Later files override values from earlier files using deep merge:

```sh
$ jinja2 template.j2 base.json overrides.yaml production.json
```

Example with nested structure:

`base.json`:
```json
{
  "app": "myapp",
  "server": {
    "host": "localhost",
    "port": 3000
  },
  "debug": false
}
```

`production.yaml`:
```yaml
server:
  port: 8080
debug: false
```

Result after merge:
```json
{
  "app": "myapp",
  "server": {
    "host": "localhost",
    "port": 8080
  },
  "debug": false
}
```

Note that `server.host` is preserved from `base.json` while `server.port` is overridden by `production.yaml`.

## Inline variables
```sh
$ jinja2 template.j2 data.json --format json -D foo=bar -D answer=42
```

### Nested variables with dot notation
Use dot notation to set nested dictionary values:
```sh
$ jinja2 template.j2 data.json -D server.host=localhost -D server.port=8080
```

This is equivalent to:
```json
{
  "server": {
    "host": "localhost",
    "port": "8080"
  }
}
```

Dot notation merges with existing data, so you can override specific nested values without replacing the entire structure.

## Environment variables
Template:
```
PATH is {{ environ('PATH') }}
USER is {{ environ('USER') }}
USERNAME is {{ environ('USERNAME') }}
```

Run:
```sh
$ jinja2 template.j2 - --format env <<'EOF'
PATH=$PATH
USER=$USER
USERNAME=$USERNAME
EOF
```

## Extensions
```sh
$ jinja2 template.j2 data.json -e do -e loopcontrols
$ jinja2 template.j2 data.json -e myext:MyExtension
```

See [extensions.md](extensions.md) for details.

## Custom Filters
```sh
# Import a custom filter module
$ jinja2 template.j2 data.json -F myfilters

# Import specific filter function
$ jinja2 template.j2 data.json -F myfilters.reverse

# Use Ansible filters
$ jinja2 template.j2 data.json -F ansible.plugins.filter.core
```

See [filters.md](filters.md) for detailed examples and patterns.

## Include paths
Use `-I` to add directories to the template search path. This is useful when
templates need to include or import from a shared directory:

```
project/
├── templates/
│   ├── macros/
│   │   └── buttons.j2
│   └── pages/
│       └── home.j2
└── data.json
```

`home.j2`:
```jinja
{% from "macros/buttons.j2" import button %}
{{ button("Click me") }}
```

```
$ jinja2 templates/pages/home.j2 data.json -I templates/
```

## Stream mode
Use `-S` to read the template from stdin, useful for one-liners:
```
$ echo '{{ 1 + 1 }}' | jinja2 -S
2

$ echo 'Hello {{ name }}!' | jinja2 -S -D name=world
Hello world!

$ echo 'Home: {{ environ("HOME") }}' | jinja2 -S
Home: /home/user
```

Stream mode also supports data files:
```
$ echo 'Hello {{ name }}!' | jinja2 -S data.json
Hello World!

$ echo '{{ greeting }} {{ name }}!' | jinja2 -S base.json overrides.yaml
Hello World!
```

## In the wild

### Dangerzone
[Freedom of the Press Foundation](https://freedom.press/) uses jinja2-cli to
generate Dockerfiles for [Dangerzone](https://github.com/freedomofpress/dangerzone),
a tool for converting potentially dangerous PDFs into safe ones.

See: [Makefile](https://github.com/freedomofpress/dangerzone/blob/main/Makefile)
```make
poetry run jinja2 Dockerfile.in Dockerfile.env > Dockerfile
```

### Elastic Docker Images
Elastic uses jinja2-cli to generate Dockerfiles and docker-compose configs for
their official [Beats](https://github.com/elastic/beats-docker),
[Logstash](https://github.com/elastic/logstash-docker), and
[Kibana](https://github.com/elastic/kibana-docker) Docker images.

See: [beats-docker Makefile](https://github.com/elastic/beats-docker/blob/master/Makefile)
```make
jinja2 -D beat=$@ -D elastic_version=$(ELASTIC_VERSION) \
  templates/Dockerfile.j2 > build/$@/Dockerfile-full
```

### ScyllaDB
[ScyllaDB](https://www.scylladb.com/) uses jinja2-cli in their
[machine image tooling](https://github.com/scylladb/scylla-machine-image) for
generating cloud deployment configurations.

---

Have a public example? Add a link here.
