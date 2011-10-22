#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from functools import wraps
from os import listdir
from os.path import dirname, join, realpath

from flask import Flask, redirect, request
from jinja2 import Template


# set file system paths
CURR_DIR = dirname(realpath(__file__))
BUILD_DIR = join(CURR_DIR, 'build')
TEMPLATES_DIR = join(CURR_DIR, 'templates')

# list available website paths
PATHS = []
ext = '.html'
ext_len = len(ext)
for prefix in ['', 'tags/']:
    for name in listdir(join(BUILD_DIR, prefix)):
        if name.endswith(ext):
            PATHS.append(prefix + name[:-ext_len])

# get latest post's path
LATEST_POST_PATH = sorted(filter(lambda s: s[0] == '2', PATHS))[-1]

# get wrapping template
with open(join(TEMPLATES_DIR, 'wrapper.html')) as f:
    WRAPPER = Template(f.read())

# create wsgi app
app = Flask(__name__)


@app.route('/')
def flipflop_ninja():
    return redirect(LATEST_POST_PATH)


@app.route('/<path:path>')
def bohemian_behemoth(path):
    if path.endswith('/'):
        return redirect(path.rstrip('/'))

    if path not in PATHS:
        return '404', 404

    if 'X-PJAX' in request.headers:
        return html_for(path)
    else:
        return wrap(html_for(path))


# only in dev
@app.route('/static/<path:path>')
def threadsafeghostbustersandwichfactory(path):
    return app.send_static_file(path)


def abomimemonationize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper


@abomimemonationize
def html_for(path):
    with open(join(BUILD_DIR, path + '.html')) as f:
        return f.read()


def wrap(sth):
    return WRAPPER.render(inner=sth, debug=app.debug)


# populate cache
for path in PATHS:
    html_for(path)


if __name__ == '__main__':
    app.run(debug=True)
