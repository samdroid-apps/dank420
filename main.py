#!/usr/bin/env python3

from dank420 import Site, View, Pathspec
from dank420 import static
from dank420 import collection
import subprocess


site = Site()

class BasicCollection(collection.Collection):
    class Item(collection.Item):
        pass

    def load(self):
        pass

    def __iter__(self):
        return iter([
            self.Item(a=10, b=2), self.Item(a=20, b=1), self.Item(a=30, b=3)])


posts = BasicCollection()


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
        return f'/blog/{item.a}'


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
