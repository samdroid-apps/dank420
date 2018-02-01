#!/usr/bin/env python3

from dank420 import Site, View, Pathspec
from dank420 import static
from dank420 import collection
from dank420 import util
import re
import markdown
import pygments
import pygments.formatters
import pygments.lexers
import frontmatter
import scss


site = Site()

class CodeBlockPreprocessor(markdown.preprocessors.Preprocessor):
    """
    Adapted from:
    https://bitbucket.org/birkenfeld/pygments-main/ \
        src/e79a7126551c39d5f8c1b83a79c14e86992155a4/external/markdown-processor.py

    Later adapted from:
    https://github.com/grow/grow/blob/0.3.7/grow/common/markdown_extensions.py#L130-L198
    """
    KIND = 'sourcecode'
    pattern_ticks = re.compile(r'```(?P<lang>.*?)\n(?P<content>.+?)\n```', re.S)

    def __init__(self, markdown_instance):
        self.markdown = markdown_instance
        self.formatter = pygments.formatters.HtmlFormatter(noclasses=True)

    def run(self, lines):
        class_name = 'code'

        def repl(match):
            language = match.group('lang')
            if not language:
                language = 'text'

            content = match.group('content')
            lexer = pygments.lexers.get_lexer_by_name(language)
            code = pygments.highlight(content, lexer, self.formatter)
            return f'\n\n<div class="{class_name}">{code}</div>\n\n'

        content = '\n'.join(lines)
        content = self.pattern_ticks.sub(repl, content)
        return content.split('\n')


class CodeBlockExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.processor = CodeBlockPreprocessor(md)
        self.processor.md = md
        md.preprocessors.add('sourcecode', self.processor, '_begin')

markdown_ctx = markdown.Markdown(extensions=[CodeBlockExtension()])

class PostsCollection(collection.FileCollection):
    path = './posts/**.md'

    class Item(collection.FileCollectionItem):
        def __init__(self, fname):
            post = frontmatter.load(fname)
            super().__init__(fname, content=post.content, **post.metadata)

        @property
        def main_url(self):
            if hasattr(self, 'url'):
                return self.url
            else:
                slug = util.slugify_grow(self.title)
                return f'/blog/{slug}'

        @property
        def html(self):
            return markdown_ctx.convert(self.content)


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
            data = scss.compiler.compile_file(path)
            return data.encode()
        else:
            return super().read_path(path)


site.cli()
