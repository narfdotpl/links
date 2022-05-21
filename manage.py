#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager
from os.path import dirname, join, realpath
from os import system
from sys import argv


CURR_DIR = dirname(realpath(__file__))
APP_DIR = join(CURR_DIR, 'app')
LOGS_DIR = join(CURR_DIR, 'logs')

TASKS = {}


def task(func):
    TASKS[func.__name__] = func
    return func


@contextmanager
def lcd(path):
    def local(cmd):
        system('cd "%s" && %s' % (path, cmd))

    yield local


@task
def build_static():
    'build js and css'

    with lcd(APP_DIR) as local:
        # js
        local('cp -r vendor static')
        local('coffee --print static-src/app.coffee | uglifyjs > static/app.js')

        # css
        local('sass static-src/style.sass > static/style.css')


@task
def deploy():
    'update production with latest changes'

    logs_fetch()
    system('git push --force-with-lease dokku HEAD:master')
    visit()


@task
def runserver():
    'run locally'

    prefix = 'PYTHONPATH="${PYTHONPATH}:$(pwd)" '

    with lcd(CURR_DIR) as local:
        local(prefix + 'python app/generator.py &')
        local('f() { sleep 0.2; open http://localhost:8000; }; f &')
        local(prefix + 'python app/server.py')


@task
def logs_fetch():
    # logs start at the last deployment
    with lcd(LOGS_DIR) as local:
        local("ssh dokku -t 'docker logs $(cat /home/dokku/links/CONTAINER.web.1)' | gzip > $(date +%Y-%m-%d_%H%M).txt.gz")


@task
def logs_show():
    with lcd(LOGS_DIR) as local:
        local("gunzip -c $(ls *.txt.gz) | ag -v 'GET /static' | goaccess -o html > index.html && open index.html")


@task
def publish():
    'publish to GitHub and deploy to production'

    deploy()
    system('git push')


@task
def visit():
    'visit links.narf.pl'
    system('open http://links.narf.pl/')


if __name__ == '__main__':
    TASKS[argv[1]]()
