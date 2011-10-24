#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from collections import defaultdict
from os import listdir, mkdir
from os.path import dirname, exists, join, realpath
from shutil import rmtree

from jinja2 import Template
import yaml


# set paths
CURR_DIR = dirname(realpath(__file__))
BUILD_DIR = join(CURR_DIR, 'build')
POSTS_DIR = join(CURR_DIR, '..', 'posts')
TAGS_DIR = join(BUILD_DIR, 'tags')
TEMPLATES_DIR = join(CURR_DIR, 'templates')

# keep templates in memory
templates = {}
for name in ['link', 'post', 'tag', 'tags']:
    with open(join(TEMPLATES_DIR, '%s.html' % name)) as f:
        templates[name] = Template(f.read())


class Link(object):

    def __init__(self, dct, post):
        self._dct = dct
        self.tags = map(Tag, dct['tags'])
        self.tags.append(Tag('_post', post))

        self._dct['desc'] = self._dct.get('desc', '').replace('\n', '<br>')

    def __getattr__(self, name):
        return self._dct.get(name)


class Post(object):

    def __init__(self, date, prev, next, src):
        self.date = date
        self.prev = '/%s' % prev if prev else None
        self.next = '/%s' % next if next else None
        self.url = '/%s' % date
        self.path = join(BUILD_DIR, '%s.html' % date)
        self.links = (Link(dct, self) for dct in yaml.load(open(src)))


class Tag(object):

    def __init__(self, name, post=None):
        self.name = name
        self.post = post
        self.url = post.url if post else '/tags/%s' % name
        self.path = join(TAGS_DIR, '%s.html' % name)


def get_posts():
    ext = '.yaml'
    names = [ext]
    names.extend(sorted([x for x in listdir(POSTS_DIR) if
                         x.endswith('yaml') and not x.startswith('.')],
                        reverse=True))
    names.append(ext)

    for i in xrange(1, len(names) - 1):
        next, date, prev = [names[i + j][:-len(ext)] for j in [-1, 0, 1]]
        yield Post(date, prev, next, join(POSTS_DIR, names[i]))


def render(a1, a2=None):
    if isinstance(a1, (Link, Post, Tag)):
        name = a1.__class__.__name__.lower()
    else:
        name = 'tags'

    kw = {name: a1}

    if isinstance(a1, Link):
        kw['current_tag_name'] = a2.name if a2 else '_post'

    return templates[name].render(kw)


def _main():
    # start with clear build dir
    if exists(BUILD_DIR):
        rmtree(BUILD_DIR)
    mkdir(BUILD_DIR)
    mkdir(TAGS_DIR)

    # prepare to count tag occurances
    tags_count = defaultdict(int)

    # render posts creating tag pages as you go by
    for post in get_posts():

        with open(post.path, 'w') as post_f:
            post_f.write(render(post))

            for link in post.links:
                post_f.write(render(link))

                for tag in link.tags[:-1]:
                    tags_count[tag.name] += 1
                    is_new = not exists(tag.path)

                    with open(tag.path, 'a') as tag_f:
                        if is_new:
                            tag_f.write(render(tag))

                        tag_f.write(render(link, tag))

    # create histogram bars for tags
    tags = []
    for name, count in tags_count.iteritems():
        tags.append({'name': name, 'bar': '&middot;' * count})

    # render tags list
    tags.sort(key=lambda dct: (-len(dct['bar']), dct['name']))
    with open(join(BUILD_DIR, 'tags.html'), 'w') as f:
        f.write(render(tags))


if __name__ == '__main__':
    _main()
