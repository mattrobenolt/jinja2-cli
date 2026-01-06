# Extensions

## Built-in extensions
You can pass built-ins by short name:
```
$ jinja2 template.j2 data.json -e do -e loopcontrols
```

## Local extensions
For local modules, use `module:ClassName` and keep the module in the working
folder. The CLI will attempt to load the module from the current directory if
it is not importable.
```
$ jinja2 template.j2 data.json -e myext:MyExtension
```

## Installed extensions
If the extension module is importable (installed or on `PYTHONPATH`), it is
loaded from the environment instead of the working directory.
