#!/usr/bin/env python
# encoding: utf-8

from __future__ import division

from flask import Flask, redirect


# create wsgi app
app = Flask(__name__)


@app.route('/')
def flipflop_ninja():
    return redirect('')


@app.route('/<path:path>')
def bohemian_behemoth(path):
    return redirect('')


if __name__ == '__main__':
    app.run(debug=True)
