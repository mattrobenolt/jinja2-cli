# Custom Filters

Custom filters allow you to extend Jinja2's built-in filters with your own Python functions.

## Quick Start

```bash
# Import a single filter function
$ jinja2 template.j2 data.json -F mymodule.myfilter

# Import all filters from a module
$ jinja2 template.j2 data.json -F mymodule
```

## Writing Custom Filters

Create a Python module with filter functions:

```python
# myfilters.py
def reverse(s):
    """Reverse a string"""
    return s[::-1]

def uppercase(s):
    """Convert to uppercase"""
    return s.upper()

def multiply(value, factor=2):
    """Multiply a value by a factor"""
    return value * factor
```

Use in your template:

```jinja2
{{ "hello" | reverse }}
{{ "hello" | uppercase }}
{{ 5 | multiply(3) }}
```

Run:

```bash
$ jinja2 template.j2 data.json -F myfilters
```

## Import Patterns

### Auto-discovery from module

Import all public functions from a module:

```bash
$ jinja2 template.j2 data.json -F myfilters
```

This will import all functions that don't start with `_`.

### Specific function

Import just one filter function:

```bash
$ jinja2 template.j2 data.json -F myfilters.reverse
```

### Multiple filters

Import from multiple modules or functions:

```bash
$ jinja2 template.j2 data.json -F myfilters.reverse -F otherfilters.double
```

### Filters dict

If your module has a `filters` dict, it will be used:

```python
# myfilters.py
def reverse(s):
    return s[::-1]

def shout(s):
    return s.upper() + "!"

filters = {
    'reverse': reverse,
    'shout': shout,
}
```

```bash
$ jinja2 template.j2 data.json -F myfilters
# or explicitly reference the dict
$ jinja2 template.j2 data.json -F myfilters.filters
```

### Loader functions

Functions starting with `load_` or named `filters`, `get_filters`, or `load_filters` are treated as loader functions that return a dict of filters:

```python
# myfilters.py
def load_custom_filters():
    return {
        'reverse': lambda s: s[::-1],
        'double': lambda n: n * 2,
    }
```

```bash
$ jinja2 template.j2 data.json -F myfilters.load_custom_filters
```

## Using Ansible Filters

Ansible filters are supported with special handling for the `FilterModule` pattern:

### Simplified syntax

```bash
# Load all Ansible core filters
$ jinja2 template.j2 data.json -F ansible.plugins.filter.core

# Load ipaddr filters
$ jinja2 template.j2 data.json -F ansible.plugins.filter.ipaddr

# Load netaddr filters
$ jinja2 template.j2 data.json -F ansible.plugins.filter.netaddr
```

### Explicit FilterModule class

```bash
$ jinja2 template.j2 data.json -F ansible.plugins.filter.core.FilterModule
```

### Example template using Ansible filters

```jinja2
{# Using the combine filter #}
{% set defaults = {'port': 8080, 'host': 'localhost'} %}
{% set custom = {'port': 3000} %}
{{ defaults | combine(custom) | to_json }}

{# Using ipaddr filter #}
{{ '192.168.1.1' | ipaddr }}
```

```bash
$ jinja2 template.j2 data.json -F ansible.plugins.filter.core -F ansible.plugins.filter.ipaddr
```

## Local vs Installed Modules

### Installed modules

If a module is importable (installed via pip or on `PYTHONPATH`), it will be loaded from the environment:

```bash
$ pip install my-custom-filters
$ jinja2 template.j2 data.json -F my_custom_filters
```

### Local modules

If the module is not importable, jinja2-cli will look for it in the current directory:

```
project/
├── filters/
│   └── custom.py
├── template.j2
└── data.json
```

```bash
$ cd project
$ jinja2 template.j2 data.json -F filters.custom
```

## Advanced: Filter Classes

Classes with a `filters()` method are automatically instantiated and their filters are loaded:

```python
# myfilters.py
class FilterModule:
    """Ansible-style filter module"""
    
    def filters(self):
        return {
            'my_filter': self.my_filter,
            'my_other_filter': self.my_other_filter,
        }
    
    def my_filter(self, value):
        return value.upper()
    
    def my_other_filter(self, value):
        return value[::-1]
```

```bash
$ jinja2 template.j2 data.json -F myfilters.FilterModule
# or let auto-discovery find it
$ jinja2 template.j2 data.json -F myfilters
```

## Real-world Examples

### Network configuration with Ansible filters

```jinja2
{# template.j2 #}
{% for interface in interfaces %}
interface {{ interface.name }}
  ip address {{ interface.ip | ipaddr('address') }}
  netmask {{ interface.ip | ipaddr('netmask') }}
{% endfor %}
```

```bash
$ jinja2 template.j2 network.json -F ansible.plugins.filter.ipaddr
```

### Data transformation

```python
# transforms.py
import json
from datetime import datetime

def to_timestamp(date_string, format='%Y-%m-%d'):
    """Convert date string to Unix timestamp"""
    dt = datetime.strptime(date_string, format)
    return int(dt.timestamp())

def pretty_json(obj):
    """Pretty-print JSON"""
    return json.dumps(obj, indent=2)

def flatten(nested_list):
    """Flatten a nested list"""
    return [item for sublist in nested_list for item in sublist]
```

```jinja2
{# template.j2 #}
{{ date | to_timestamp }}
{{ data | pretty_json }}
{{ nested | flatten | join(', ') }}
```

```bash
$ jinja2 template.j2 data.json -F transforms
```
