#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from os.path import dirname, join, realpath

from fabric.api import cd, env, local, run, task
from fabric.contrib.project import rsync_project as rsync


CURR_DIR = dirname(realpath(__file__))
APP_DIR = join(CURR_DIR, 'app')

env.hosts = ['narf@narf.megiteam.pl']


@task
def build():
    'generate html from yaml'

    def in_app_dir(*args):
        cmd = "cd '%s' && " % APP_DIR
        local(cmd + ' '.join(args))

    # html
    in_app_dir('python generator.py')

    # js
    in_app_dir('cp -r vendor static')
    in_app_dir('coffee --print static-src/app.coffee | uglifyjs '
               '> static/app.js')

    # css
    css = 'static/style.css'
    in_app_dir('cp static-src/reset.css', css)
    in_app_dir('sass static-src/style.sass >>', css)


@task
def deploy():
    'update production with latest changes'
    # aka build, push, pull, install, rsync, restart, visit

    build()
    local('git push')

    with cd('~/narf.pl/links/depl'):
        run('git pull')
        run('source .environment && pip install -r ../env/reqs')

    for subdir_name in ['build', 'static']:
        rsync(local_dir=join(APP_DIR, subdir_name),
              remote_dir='~/narf.pl/links/app',
              delete=True)

    restart()
    visit()


@task
def restart():
    'restart production'
    run('restart-app links')


@task
def test():
    'run locally'
    build()
    local('open http://localhost:5000/')
    local("python '%s'" % join(APP_DIR, 'server.py'))


@task
def visit():
    'visit links.narf.pl'
    local('open http://links.narf.pl/')


if __name__ == '__main__':
    print 'run "fab --list"'
