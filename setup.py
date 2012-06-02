#!/usr/bin/env python
"""
jinja2-cli
======

A CLI interface to jinja2.

$ jinja2 helloworld.tmpl data.json --format=json
$ cat data.json | jinja2 helloworld.tmpl
$ curl -s http://httpbin.org/ip | jinja2 helloip.tmpl
$ curl -s http://httpbin.org/ip | jinja2 helloip.tmpl > helloip.html
"""

from setuptools import setup, find_packages

setup(
    name='jinja2-cli',
    version='0.1.1-dev',
    author='Matt Robenolt',
    author_email='matt@ydekproductions.com',
    url='https://github.com/mattrobenolt/jinja2-cli',
    description='A CLI interface to Jinja2',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    license='BSD',
    install_requires=[
        'jinja2',
        'simplejson',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jinja2 = jinja2cli:main',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
