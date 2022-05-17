#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from functools import wraps
from os import listdir
from os.path import dirname, join, realpath

from flask import Flask, make_response, redirect, request
from jinja2 import Template

from common import open


# set file system paths
CURR_DIR = dirname(realpath(__file__))
BUILD_DIR = join(CURR_DIR, 'build')
TEMPLATES_DIR = join(CURR_DIR, 'templates')

# list available website paths
PATHS = ['feed']
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

# read 404 page
with open(join(TEMPLATES_DIR, '404.html')) as f:
    html_for_404 = f.read()

# create wsgi app
app = Flask(__name__)


@app.route('/')
def flipflop_ninja():
    return redirect(LATEST_POST_PATH)


@app.route('/<path:path>')
def bohemian_behemoth(path):
    if path.endswith('/'):
        return redirect(path.rstrip('/'), 301)

    if path not in PATHS:
        return html_for_404, 404

    if path == 'feed':
        return teenage_mutant_ninja_burrito()

    return wrap(html_for(path))


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
    return takeaway(path + '.html')


@abomimemonationize
def teenage_mutant_ninja_burrito():
    response = make_response(takeaway('feed.xml'))
    response.mimetype = 'application/atom+xml'
    return response


def takeaway(path):
    with open(join(BUILD_DIR, path)) as f:
        return f.read()


def wrap(sth):
    return WRAPPER.render(debug=app.debug, latest=LATEST_POST_PATH, inner=sth)


# populate cache
for path in PATHS[1:]:
    html_for(path)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
