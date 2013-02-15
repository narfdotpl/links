#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from os.path import dirname, join, realpath

from fabric.api import cd, env, local, run, task


CURR_DIR = dirname(realpath(__file__))
APP_DIR = join(CURR_DIR, 'app')

env.hosts = ['narf@narf.megiteam.pl']


@task
def deploy():
    'update production with latest changes'

    local('git push')

    with cd('~/narf.pl/ln/depl'):
        run('git pull')
        run('source .environment && pip install -r ../env/reqs')

    restart()
    visit()


@task
def restart():
    'restart production'
    run('restart-app ln')


@task
def test():
    'run locally'
    local('open http://localhost:5000/')
    local("python '%s'" % join(APP_DIR, 'server.py'))


@task
def visit():
    'visit ln.narf.pl'
    local('open http://ln.narf.pl/')


if __name__ == '__main__':
    print 'run "fab --list"'
