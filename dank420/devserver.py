import sys
import http.server
from werkzeug import wrappers
from werkzeug import serving
from werkzeug.contrib.profiler import ProfilerMiddleware

from .response import force_response, Response
from .request import Request


class DevServer():
    def __init__(self, site):
        self.site = site

    @wrappers.Request.application
    def wsgi_app(self, request):
        if request.method not in ['HEAD', 'GET']:
            return wrappers.Response(b'Method not allowed', status=405)

        path = request.path
        response, status = self.dispatch(path)
        return wrappers.Response(
                response.data,
                status=status,
                mimetype=response.content_type)

    def dispatch(self, path: str) -> Response:
        handler = self.site.router.find(path)
        if handler is None:
            return Response(b'404 no matching handler; use the `paths` subcommand to debug'), 404
        else:
            request = Request(path, self.site)
            resp = force_response(handler.dispatch(request))
            return resp, 200


def run_dev_server(my_site, host, port, profile=False):
    app = DevServer(my_site).wsgi_app

    if profile:
        app = ProfilerMiddleware(app)

    serving.run_simple(
        host, port, app,
        use_debugger=True,
        use_reloader=True)
