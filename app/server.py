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

# create wsgi app
app = Flask(__name__)


def abomimemonationize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if app.debug:
            return func(*args)

        if args not in cache:
            cache[args] = func(*args)

        return cache[args]

    return wrapper


# get wrapping template
with open(join(TEMPLATES_DIR, 'wrapper.html')) as f:
    WRAPPER = Template(f.read())

# read 404 page
with open(join(TEMPLATES_DIR, '404.html')) as f:
    html_for_404 = f.read()


@abomimemonationize
def get_paths():
    paths = ['feed']
    ext = '.html'
    ext_len = len(ext)
    for prefix in ['', 'tags/']:
        for name in listdir(join(BUILD_DIR, prefix)):
            if name.endswith(ext):
                paths.append(prefix + name[:-ext_len])

    return paths


def get_latest_post_path():
    return sorted(filter(lambda s: s[0] == '2', get_paths()))[-1]


@app.route('/')
def flipflop_ninja():
    return redirect(get_latest_post_path())


@app.route('/<path:path>')
def bohemian_behemoth(path):
    if path.endswith('/'):
        return redirect(path.rstrip('/'), 301)

    if path not in get_paths():
        return html_for_404, 404

    if path == 'feed':
        return teenage_mutant_ninja_burrito()

    return wrap(html_for(path))


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
    return WRAPPER.render(debug=app.debug, latest=get_latest_post_path(), inner=sth)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
else:
    # populate cache
    for path in get_paths()[1:]:
        html_for(path)
