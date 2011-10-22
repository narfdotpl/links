#!/usr/bin/env python
# encoding: utf-8

from __future__ import division

from fabric.api import cd, env, local, run, task


env.hosts = ['narf@narf.megiteam.pl']


@task
def deploy():
    'update production with latest changes'
    # aka push, pull, install, restart, visit

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
def visit():
    'visit ln.narf.pl'
    local('open http://ln.narf.pl/')


if __name__ == '__main__':
    print 'run "fab --list"'
