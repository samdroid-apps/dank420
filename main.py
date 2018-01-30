#!/usr/bin/env python3

from dank420 import Site, View, Pathspec, StaticView
import subprocess


site = Site()

@site.register
class IndexView(View):
    def dispatch(self, request):
        return request.site.templates.render('index.html')

    def get_all_paths(self):
        return ['/']


@site.register
class BlogPostView(View):
    pathspec = Pathspec('/blog/<post>')

    def dispatch(self, request):
        data = self.pathspec.match(request.path)
        return 'Viewing blog post: {}'.format(data['post'])

    def get_all_paths(self):
        names = ['post-1']
        return [self.pathspec.format(post=name) for name in names]


@site.register
class MyStaticView(StaticView):
    template_filter_name = 'static_url'
    base = 'static'
    pathspec = Pathspec('/static/<*name>')

    def read_path(self, path):
        if path.endswith('.scss'):
            return subprocess.check_output(['scss', path])
        else:
            return super().read_path(path)


site.cli()
