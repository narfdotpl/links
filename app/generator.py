#!/usr/bin/env python
# encoding: utf-8

from collections import defaultdict
from os import listdir, mkdir, symlink
from os.path import dirname, exists, join, realpath
from shutil import rmtree

from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader
from markdown import markdown as render_markdown
import typogrify.filters
import yaml

from app.common import open


# set paths
CURR_DIR = dirname(realpath(__file__))
STATIC_DIR = join(CURR_DIR, 'static')
BUILD_DIR = join(CURR_DIR, 'build')
POSTS_DIR = join(CURR_DIR, '..', 'posts')
TAGS_DIR = join(BUILD_DIR, 'tags')

env = Environment(loader=PackageLoader("app"))
wrapper_template = env.get_template('wrapper.html')


class Note:
    def __init__(self, dct):
        self.html = improve_typography(render_markdown(dct['text']))

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
        self.post = post

    def __getattr__(self, name):
        return self._dct.get(name)


class Post(object):

    def __init__(self, date, prev, next, src):
        self.date = date
        self.prev = '/%s' % prev if prev else None
        self.next = '/%s' % next if next else None
        self.url = '/%s' % date
        self.path = join(BUILD_DIR, '%s.html' % date)

        self.items = []
        for dct in yaml.load(open(src), yaml.Loader):
            if dct.get('type') == 'note':
                self.items.append(Note(dct))
            else:
                self.items.append(Link(dct, self))


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


def render_and_write_html(filename, output_filename=None, **kw):
    template = env.get_template(filename)
    html = template.render(kw)
    html = strip_whitespace_from_links(html)
    html = wrapper_template.render(inner=html)

    with open(join(BUILD_DIR, output_filename or filename), 'w') as f:
        f.write(html)


def render_and_write(filename, **kw):
    with open(join(BUILD_DIR, filename), 'w') as f:
        f.write(env.get_template(filename).render(kw))


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

    # symlink static files
    symlink(STATIC_DIR, join(BUILD_DIR, 'static'))

    # prepare to count tag occurances
    links_by_tag_name = defaultdict(list)
    total_link_count = 0
    total_years = set()

    posts = list(get_posts())
    render_and_write('index.html', latest=posts[0].date)

    for post in posts:
        render_and_write_html("post.html", post.path, post=post, current_tag_name='_post')

        # track tags
        for item in post.items:
            if isinstance(item, Link):
                link = item
                total_link_count += 1
                for tag in link.tags[:-1]:
                    links_by_tag_name[tag.name].append(link)

    for (tag_name, links) in links_by_tag_name.items():
        years = {int(link.post.date.split('-')[0]) for link in links}
        total_years |= years
        render_and_write_html("tag.html", f'tags/{tag_name}.html',
            tag_name=tag_name,
            current_tag_name=tag_name,
            links=links,
            start_year=min(years),
            end_year=max(years),
        )

    # prepare to create a tag cloud
    tags_count = {tag: len(links) for (tag, links) in links_by_tag_name.items()}
    min_count = min(tags_count.values())
    max_count = max(tags_count.values())
    min_scale = 1.0
    max_scale = 3.0
    f = lambda n: min(200, n)
    get_scale = lambda count: '%.2f' % mix(f(count), f(min_count), f(max_count), min_scale, max_scale)

    # render tag cloud
    render_and_write_html('tags.html',
        link_count=total_link_count,
        start_year=min(total_years),
        end_year=max(total_years),
        tags=[
            {'name': tag, 'scale': get_scale(count)} \
            for tag, count in sorted(tags_count.items())
        ]
    )

    # render feed
    render_and_write('feed.xml', dates=[p.date for p in posts])


if __name__ == '__main__':
    _main()
