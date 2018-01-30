#!/usr/bin/env python3

from dank420 import Site, View, Pathspec
from dank420 import static
from dank420 import collection
import glob
import subprocess
import frontmatter


site = Site()

class PostsCollection(collection.FileCollection):
    path = './posts/**.md'

    class Item(collection.FileCollectionItem):
        def __init__(self, fname):
            post = frontmatter.load(fname)
            super().__init__(fname, content=post.content, **post.metadata)

        @property
        def main_url(self):
            return f'/blog/{self.order}'


posts = PostsCollection().sort('order')


@site.register
class IndexView(View):
    def dispatch(self, request):
        return request.site.templates.render('index.html', posts=posts)

    def get_all_paths(self):
        return ['/']


@site.register
class BlogPostView(collection.ItemPerPageView):
    collection = posts

    def dispatch(self, request):
        item = self.get_item_for_request(request)
        return request.site.templates.render('post.html', post=item)

    def get_path_for_item(self, item):
        return item.main_url


@site.register
class MyStaticView(static.StaticView):
    template_filter_name = 'static_url'
    base = 'static'
    pathspec = Pathspec('/static/<*name>')

    def read_path(self, path):
        if path.endswith('.scss'):
            return subprocess.check_output(['scss', path])
        else:
            return super().read_path(path)


site.cli()
