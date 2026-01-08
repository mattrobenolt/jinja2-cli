# Docker

The official jinja2-cli Docker image is available at `ghcr.io/mattrobenolt/jinja2`.

## Installation

Pull the latest image:

```bash
docker pull ghcr.io/mattrobenolt/jinja2:latest
```

Or use a specific version:

```bash
docker pull ghcr.io/mattrobenolt/jinja2:1.0.0
```

## Usage

### Basic Example

Mount your template and data files, then pass them as arguments:

```bash
docker run --rm \
  -v $PWD:/workspace \
  ghcr.io/mattrobenolt/jinja2:latest \
  /workspace/template.j2 /workspace/data.json
```

### Using stdin

Pipe a template via stdin using stream mode:

```bash
echo 'Hello {{ name }}!' | docker run --rm -i \
  ghcr.io/mattrobenolt/jinja2:latest \
  -S -D name=World
```

### With environment variables

Pass environment variables and access them in templates:

```bash
docker run --rm \
  -v $PWD:/workspace \
  -e DATABASE=mysql \
  -e VERSION=1.0 \
  ghcr.io/mattrobenolt/jinja2:latest \
  /workspace/config.j2
```

Template:
```jinja2
database: {{ environ('DATABASE') }}
version: {{ environ('VERSION') }}
```

### Output to file

Redirect output to a file on the host:

```bash
docker run --rm \
  -v $PWD:/workspace \
  ghcr.io/mattrobenolt/jinja2:latest \
  /workspace/template.j2 /workspace/data.yaml --format yaml \
  > output.txt
```

Or use the `-o` flag to write inside the container's filesystem:

```bash
docker run --rm \
  -v $PWD:/workspace \
  ghcr.io/mattrobenolt/jinja2:latest \
  /workspace/template.j2 /workspace/data.json \
  -o /workspace/output.txt
```

### Multiple data files

Mount multiple data files and they'll be deep merged:

```bash
docker run --rm \
  -v $PWD:/workspace \
  ghcr.io/mattrobenolt/jinja2:latest \
  /workspace/template.j2 \
  /workspace/base.json \
  /workspace/override.yaml \
  /workspace/production.json
```

## Image Details

- **Base**: Chainguard Wolfi (minimal, secure)
- **Architectures**: `linux/amd64`, `linux/arm64`
- **User**: Runs as non-root user
- **Size**: ~90MB
- **Includes**: All optional dependencies (yaml, toml, xml, hjson, json5)

## Available Tags

- `latest` - Latest stable release
- `main` - Latest commit on main branch (development)
- `1`, `1.0`, `1.0.0` - Semantic versioning tags

## CI/CD Usage

The image is useful in CI/CD pipelines for generating configuration files:

### GitHub Actions

```yaml
- name: Generate config
  run: |
    docker run --rm \
      -v ${{ github.workspace }}:/workspace \
      ghcr.io/mattrobenolt/jinja2:latest \
      /workspace/config.j2 /workspace/vars.json \
      -o /workspace/config.yml
```

### GitLab CI

```yaml
generate-config:
  image: ghcr.io/mattrobenolt/jinja2:latest
  script:
    - jinja2 template.j2 data.json -o config.yml
  artifacts:
    paths:
      - config.yml
```

## Tips

1. **Mount volumes** at `/workspace` or any path you prefer
2. **Use absolute paths** for template and data files (e.g., `/workspace/file.j2`)
3. **Stream mode** (`-S`) works great for piping templates via stdin
4. **Environment variables** are accessible via `environ()` function in templates
5. The image includes all optional format dependencies pre-installed
