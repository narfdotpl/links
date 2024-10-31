#!/usr/bin/env python
# encoding: utf-8

from pathlib import Path

from flask import Flask


CURRENT_DIR = Path(__file__).absolute().parent
BUILD_DIR = CURRENT_DIR / 'build'
STATIC_DIR = BUILD_DIR / 'static'

app = Flask(__name__, static_folder=STATIC_DIR)


def read_file(path):
    with open(BUILD_DIR / path) as f:
        return f.read()


@app.route('/')
def index():
    return read_file('index.html')


@app.route('/<path:path>')
def serve(path):
    if '.' not in path:
        path += '.html'

    return read_file(path)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
