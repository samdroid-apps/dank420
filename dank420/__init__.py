import os
import re
import sys
import shutil
import argparse
from pprint import pprint

from .view import View
from .pathspec import Pathspec
from .request import Request
from .router import Router
from .response import Response, force_response
from .devserver import run_dev_server
from .templates import Templates


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

    def run(self, host, port):
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
        parser = argparse.ArgumentParser()
        subcommands = parser.add_subparsers(dest='subcommand_name')
        run_parser = subcommands.add_parser('run',
                help='Serve the site on a development server')
        run_parser.add_argument('--port', default=5000, type=int,
                help='Port to run dev server on')
        run_parser.add_argument('--host', default='127.0.0.1',
                help='Host to run dev server on')
        paths_parser = subcommands.add_parser('paths',
                help='Print all paths handled by each handler')
        build_parser = subcommands.add_parser('build',
                help='Build the site into a static folder')
        build_parser.add_argument('outdir',
                help='Directory to write the static site into')
        build_parser.add_argument('--force', dest='force', action='store_true',
                help=('If --force is used and outdir exists, '
                      'outdir will be deleted prior to building'))

        argv = sys.argv[1:]
        if len(argv) == 0:
            argv = ['-h']
        args = parser.parse_args(argv)

        if args.subcommand_name == 'run':
            self.run(port=args.port, host=args.host)
        elif args.subcommand_name == 'paths':
            self.router.print_debug()
        elif args.subcommand_name == 'build':
            outdir = args.outdir
            assert outdir
            self.build(outdir, force=args.force)
