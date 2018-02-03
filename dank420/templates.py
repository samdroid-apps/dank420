import jinja2

from . import static


class Templates():
    '''
    A class that manages the template environment
    for a given site

    Attributes:

    * environment: a jinja2.Environment
    '''

    def __init__(self, site):
        self._site = site
        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader('./templates'))
        # Disable cache as it caches results of the StaticView's
        # template filter.  This results in files not loading,
        # as they have outdated hashes.
        # FIXME: re-enable the cache
        self.environment.cache = None

    def _get_globals(self):
        return {}

    def register_filter(self, name, fn):
        self.environment.filters[name] = fn

    def render(self, name, *args, **kwargs):
        '''
        Render a template to a response

        Args:
            name (str): Name of the template file (`project-root/templates/name`)

        Remaining arguments are passed to junja2
        '''
        template = self.environment.get_template(name, globals=self._get_globals())
        return template.render(*args, **kwargs)

    def render_string(self, string, *args, **kwargs):
        template = self.environment.from_string(string, globals=self._get_globals())
        return template.render(*args, **kwargs)
