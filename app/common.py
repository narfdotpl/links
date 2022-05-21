#!/usr/bin/env python
# encoding: utf-8

import codecs


def open(path, mode='r'):
    return codecs.open(path, encoding='utf-8', mode=mode)
