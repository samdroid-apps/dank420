import sys
import http.server

from .response import force_response, Response
from .request import Request


class _DevServerHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # subclassed by the caller site
    site = None

    def dispatch(self):
        handler = self.site.router.find(self.path)
        if handler is None:
            return Response(b'404 no matching handler'), 404
        else:
            request = Request(self.path, self.site)
            resp = force_response(handler.dispatch(request))
            return resp, 200
        return Response(b'500 rip'), 500

    def do_GET(self):
        resp, code = self.dispatch()
        self.send_head(resp, code)
        self.wfile.write(resp.data)

    def do_HEAD(self):
        resp, code = self.dispatch()
        self.send_head(resp, code)

    def send_head(self, resp, code):
        self.send_response(code)
        self.send_header("Content-type", resp.content_type)
        self.send_header("Content-Length", len(resp.data))
        # self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()


def run_dev_server(my_site, host, port):
    class Handler(_DevServerHTTPRequestHandler):
        site = my_site

    addr = (host, port)
    with http.server.HTTPServer(addr, Handler) as httpd:
        sa = httpd.socket.getsockname()
        serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
        print(serve_message.format(host=sa[0], port=sa[1]))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)
