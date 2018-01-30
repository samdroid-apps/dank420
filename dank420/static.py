import os
import hashlib
import glob

from .pathspec import Pathspec
from .view import View
from .response import Response

def _files_under(base):
    first_root = None
    for root, dirs, files in os.walk(base):
        first_root = first_root or root
        subfolder = root[len(first_root):].lstrip('/')

        for fname in files:
            yield os.path.join(subfolder, fname)


def _get_hash(data):
    hasher = hashlib.sha3_256()
    hasher.update(data)
    # always returns string of len 1+64
    return 'H' + hasher.hexdigest()


def _is_hash(part):
    return len(part) == 65 and part[0] == 'H'


def _insert_hash(name, hash_part):
    dirname = os.path.dirname(name)
    basename = os.path.basename(name).split('.')
    if len(basename) == 1:
        basename.append(hash_part)
    else:
        basename.insert(-1, hash_part)
    return os.path.join(dirname, '.'.join(basename))

def _extract_hash(name):
    dirname = os.path.dirname(name)
    basename = os.path.basename(name).split('.')
    hashes = [p for p in basename if _is_hash(p)]
    assert len(hashes) == 1
    basename = [p for p in basename if not _is_hash(p)]
    return os.path.join(dirname, '.'.join(basename)), hashes[0]


class StaticView(View):
    '''
    A generic View for serving static files from a directory.  Static files
    are hashed (with a hash placed in the filename), as a kind of cache-buster.

    Example usage:

        @site.register
        class MyStaticView(StaticView):
            template_filter_name = 'main_static_url'
            base = './static-files-directory'
            pathspec = Pathspec('/static/<*name>')

    Example referencing in templates:

        {{ "main.css" | 

    Attributes:

        template_filter_name (str): the name to use for the filter
            that is added to the template environment.  This filter
            converts a path (within the static file base) to a URL
        base (str): the paths on the local filesystem to a folder
            which the static files will be loaded from
        pathspec (Pathspec): a pathspec for where they should be
            served.  Must have a variable `<*name>`, being the file name
    '''
    template_filter_name = 'static_url'
    base = 'static'
    pathspec = Pathspec('/static/<*name>')

    def read_path(self, path):
        '''
        Read a given file path, returning the data as bytes

        Can be overridden to transform the data
        '''
        with open(path, 'rb') as f:
            return f.read()

    @classmethod
    def on_registered(cls, site):
        site.templates.register_filter(cls.template_filter_name, cls.template_filter)

    @classmethod
    def template_filter(cls, filename):
        self = cls()
        local_path = os.path.join(self.base, filename)
        hash_ = _get_hash(self.read_path(local_path))
        return self.pathspec.format(name=_insert_hash(filename, hash_))

    def dispatch(self, request):
        name = self.pathspec.match(request.path)['name']
        path, hash_ = _extract_hash(name)
        fp = os.path.join(self.base, path)
        data = self.read_path(fp)
        return Response(data, content_type='text/plain')

    def _hash_fp(self, fp):
        return _get_hash(self.read_path(fp))

    def get_all_paths(self):
        files = (_files_under(self.base))
        files = [_insert_hash(f, self._hash_fp(os.path.join(self.base, f))) for f in files]
        return [self.pathspec.format(name=fn) for fn in files]

    def does_include_path(self, path):
        # A slightly faster implementation that does not read every file
        match = self.pathspec.match(path)
        if match is None:
            return False
        name = match['name']
        path, hash_ = _extract_hash(name)

        try:
            data = self.read_path(os.path.join(self.base, path))
        except FileNotFoundError:
            return False

        real_hash = _get_hash(data)
        return real_hash  == hash_
