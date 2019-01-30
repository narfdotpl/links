#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from os.path import dirname, join, realpath

from fabric.api import cd, env, lcd, local, run, task
from fabric.contrib.project import rsync_project as rsync


CURR_DIR = dirname(realpath(__file__))
APP_DIR = join(CURR_DIR, 'app')

env.hosts = ['narf@narf.megiteam.pl']


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
def build():
    'generate html from yaml'

    with lcd(APP_DIR):
        local('python generator.py')


@task
def deploy():
    'update production with latest changes'
    # aka build, push, pull, install, rsync, restart, visit

    build()
    local('git push')

    with cd('~/narf.pl/links/depl'):
        run('git pull backup master')
        run('source .environment && pip install -r ../env/reqs')

    for subdir_name in ['build', 'static']:
        rsync(local_dir=join(APP_DIR, subdir_name),
              remote_dir='~/narf.pl/links/app',
              delete=True)

    restart()
    visit()


@task
def dev():
    'run locally'
    build()
    local('open http://localhost:5000/')
    local("python '%s'" % join(APP_DIR, 'server.py'))


@task
def publish():
    'publish to GitHub and deploy to production'
    deploy()


@task
def restart():
    'restart production'
    run('restart-app links')


@task
def visit():
    'visit links.narf.pl'
    local('open http://links.narf.pl/')


if __name__ == '__main__':
    print 'run "fab --list"'
