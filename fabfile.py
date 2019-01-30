#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from os.path import dirname, join, realpath

from fabric.api import cd, lcd, local, run, task


CURR_DIR = dirname(realpath(__file__))
APP_DIR = join(CURR_DIR, 'app')


@task
def build_static():
    'build js and css'

    with lcd(APP_DIR):
        # js
        local('cp -r vendor static')
        local('coffee --print static-src/app.coffee | uglifyjs > static/app.js')

        # css
        local('sass static-src/style.sass > static/style.css')


@task
def deploy():
    'update production with latest changes'

    local('git push --force-with-lease dokku HEAD:master')
    visit()


@task
def dev():
    'run locally'

    with lcd(APP_DIR):
        local('python generator.py')
        local('open http://localhost:5000/')
        local('python server.py')


@task
def publish():
    'publish to GitHub and deploy to production'

    deploy()
    local('git push')


@task
def visit():
    'visit links.narf.pl'
    local('open http://links.narf.pl/')


if __name__ == '__main__':
    print 'run "fab --list"'
