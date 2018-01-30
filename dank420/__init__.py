import os
import re
import sys
import shutil
from pprint import pprint

from .view import View
from .pathspec import Pathspec
from .request import Request
from .router import Router
from .response import Response, force_response
from .devserver import run_dev_server
from .templates import Templates
from .static import StaticView


class Site():
    '''
    Object representing a site (styles off flask's App)
    '''

    def __init__(self):
        self.router = Router()
        self.templates = Templates(self)

    def register(self, handler):
        '''
        Register a handler in the static site

        Can be used as a class decorator or a function

        Args:

            * handler (View subclass type): thing to render the route
        '''
        #if not (isinstance(handler, type) and issubclass(handler, View)):
        #    real_handler = handler
        #    class WrappedView(View):
        #        def dispatch(self, request):
        #            return real_handler(request)
        #    handler = WrappedView
        handler.on_registered(self)
        self.router.add(handler)

    def run(self, host='127.0.0.1', port=5000):
        run_dev_server(self, host, port)

    def build(self, outdir, force=False):
        if os.path.exists(outdir):
            if force:
                shutil.rmtree(outdir)
            else:
                raise Exception('Can not build; outdir exists')
        os.makedirs(outdir)

        for HandlerClass in self.router.all():
            paths = HandlerClass().get_all_paths()

            for path in paths:
                request = Request(path, self)

                handler = HandlerClass()
                resp = force_response(handler.dispatch(request))

                write_to = os.path.join(outdir, path.lstrip('/'))
                if resp.is_html and not write_to.endswith('.html'):
                    write_to = os.path.join(write_to, 'index.html')

                print('Writing:', write_to)
                os.makedirs(os.path.dirname(write_to), exist_ok=True)
                with open(write_to, 'wb') as f:
                    f.write(resp.data)

    def cli(self):
        # If I get internet access I should change this
        # to use a proper library
        if len(sys.argv) == 1:
            return self._print_help()

        command = sys.argv[1]
        if command == 'run':
            self.run()
        elif command == 'paths':
            self.router.print_debug()
        elif command == 'build':
            outdir = sys.argv[2]
            assert outdir
            self.build(outdir, force='--force' in sys.argv)
        else:
            return self._print_help()

    def _print_help(self):
        print(f'Usage: {sys.argv[0]} command')
        print()
        print(f'Commands:')
        print(f'  build outdir - Build the site and puts it into outdir')
        print(f'  paths - Print all paths')
        print(f'  run - Runs development server')
        print(f'  help - Prints this message')
