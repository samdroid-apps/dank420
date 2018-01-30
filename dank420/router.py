from .util import normalize_path

class Router():
    '''
    Router: manages the paths

    Probably not a public API
    '''

    def __init__(self):
        self._all = []

    def add(self, handler_class):
        self._all.append(handler_class)

    def find(self, path):
        path = normalize_path(path)
        for HandlerClass in self._all:
            handler = HandlerClass()
            if handler.does_include_path(path):
                return handler
        return None

    def print_debug(self):
        print('Listing all paths:')
        for HandlerClass in self._all:
            print()
            print('Handler: ', HandlerClass)
            handler = HandlerClass()
            for path in handler.get_all_paths():
                print(' -', path)

    def all(self):
        for HandlerClass in self._all:
            yield HandlerClass


