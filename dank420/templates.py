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


