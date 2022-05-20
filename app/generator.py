#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from collections import defaultdict
from os import listdir, mkdir
from os.path import dirname, exists, join, realpath
from shutil import rmtree

from bs4 import BeautifulSoup
from jinja2 import Template
from markdown import markdown as render_markdown
import typogrify.filters
import yaml

from common import open


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
        # render markdown
        desc = dct.get('desc', None)
        if desc:
            dct['desc'] = improve_typography(render_markdown(desc))

        # improve typography in title
        dct['title'] = improve_typography(dct['title'])

        self._dct = dct
        self.tags = list(map(Tag, dct['tags']))

        # automatically add "video" tag
        if 'video' not in dct['tags'] and \
                any(x in dct['link'] for x in ['youtube.com', 'vimeo.com']):
            self.tags.append(Tag('video'))

        self.tags.append(Tag('_post', post))

    def __getattr__(self, name):
        return self._dct.get(name)


class Post(object):

    def __init__(self, date, prev, next, src):
        self.date = date
        self.prev = '/%s' % prev if prev else None
        self.next = '/%s' % next if next else None
        self.url = '/%s' % date
        self.path = join(BUILD_DIR, '%s.html' % date)
        self.links = (Link(dct, self) for dct in yaml.load(open(src), yaml.Loader))


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

    for i in range(1, len(names) - 1):
        next, date, prev = [names[i + j][:-len(ext)] for j in [-1, 0, 1]]
        yield Post(date, prev, next, join(POSTS_DIR, names[i]))


def improve_typography(text):
    text = typogrify.filters.widont(text)
    text = typogrify.filters.smartypants(text)
    text = text.replace('OS X', 'OS&nbsp;X')

    return text


def render(a1, a2=None):
    name = a1.__class__.__name__.lower()
    kw = {name: a1}

    if isinstance(a1, Link):
        kw['current_tag_name'] = a2.name if a2 else '_post'

    html = templates[name].render(kw)
    html = strip_whitespace_from_links(html)

    return html


def render_and_write(filename, **kw):
    with open(join(TEMPLATES_DIR, filename)) as f:
        template = Template(f.read())

    html = template.render(kw)
    html = strip_whitespace_from_links(html)

    with open(join(BUILD_DIR, filename), 'w') as f:
        f.write(html)


def strip_whitespace_from_links(html):
    soup = BeautifulSoup(html, features='html.parser')

    for link in soup.find_all('a'):
        link.string = link.string.strip()

    return str(soup)


def mix(x, x_min, x_max, new_min, new_max):
    progress = (x - x_min) / (x_max - x_min)
    return new_min + progress * (new_max - new_min)


def _main():
    # start with clear build dir
    if exists(BUILD_DIR):
        rmtree(BUILD_DIR)
    mkdir(BUILD_DIR)
    mkdir(TAGS_DIR)

    # prepare to count tag occurances
    tags_count = defaultdict(int)

    # render posts creating tag pages as you go by
    dates = []
    for post in get_posts():
        dates.append(post.date)

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

    # prepare to create a tag cloud
    min_count = min(tags_count.values())
    max_count = max(tags_count.values())
    min_scale = 1.0
    max_scale = 3.0
    f = lambda n: min(200, n)
    get_scale = lambda count: '%.2f' % mix(f(count), f(min_count), f(max_count), min_scale, max_scale)

    # render tag cloud
    render_and_write('tags.html', tags=[
        {'name': tag, 'scale': get_scale(count)} \
        for tag, count in sorted(tags_count.items())
    ])

    # render feed
    render_and_write('feed.xml', dates=dates)


if __name__ == '__main__':
    _main()
