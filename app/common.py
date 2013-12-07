#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
import codecs


def open(path, mode='r'):
    return codecs.open(path, encoding='utf-8', mode=mode)
