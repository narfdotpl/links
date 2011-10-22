#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from os.path import dirname, join, realpath

from fabric.api import cd, env, local, run, task


CURR_DIR = dirname(realpath(__file__))

env.hosts = ['narf@narf.megiteam.pl']


@task
def build():
    'generate html from yaml'
    local("python '%s'" % join(CURR_DIR, 'app', 'generator.py'))
    local("cd '%s' && cp -r vendor static" % APP_DIR)


@task
def deploy():
    'update production with latest changes'
    # aka push, pull, install, restart, visit

    local('git push')

    with cd('~/narf.pl/ln/depl'):
        run('git pull')
        run('source .environment && pip install -r ../env/reqs && fab build')

    restart()
    visit()


@task
def restart():
    'restart production'
    run('restart-app ln')


@task
def visit():
    'visit ln.narf.pl'
    local('open http://ln.narf.pl/')


if __name__ == '__main__':
    print 'run "fab --list"'
