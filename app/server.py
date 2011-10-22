#!/usr/bin/env python
# encoding: utf-8

from __future__ import division

from flask import Flask


app = Flask(__name__)


@app.route('/')
def werter():
    return 'goodbye, cruel world!'


if __name__ == '__main__':
    app.run()
