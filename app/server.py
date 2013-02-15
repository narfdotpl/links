#!/usr/bin/env python
# encoding: utf-8

from __future__ import division

from flask import Flask, redirect


# create wsgi app
app = Flask(__name__)

base_url = 'http://links.narf.pl/'


@app.route('/')
def flipflop_ninja():
    return redirect(base_url, 301)


@app.route('/<path:path>')
def bohemian_behemoth(path):
    return redirect(base_url + path, 301)


if __name__ == '__main__':
    app.run(debug=True)
