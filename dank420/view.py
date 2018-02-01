from .util import normalize_path

class View():
    '''
    A view is something that renders paths in your site

    Do not override __init__, `dispatch` is where the action is at
    '''

    def __init__(self):
        pass

    @classmethod
    def on_registered(cls, site):
        '''
        Called when a handler is registered to a site

        Useful for doing initialization, eg. with the template context
        '''
        pass

    def dispatch(self, request):
        '''
        Get a response for a given request

        Args:
            request (Request): information about the request

        Returns: Response, str or bytes: content of this view
        '''
        raise NotImplementedError('View subclass must implement dispatch')

    def get_all_paths(self):
        '''
        Returns all paths that this view covers.

        If you are using a static path (like `/about`) it should just
        return that.  That is the default behaviour.

        You are using a more dynamic path (like `/blog/<name>`), you
        might want to override this to return a list of the paths, with
        name substituted.

        Returns:  a list of strings; all the paths
        '''
        pass

    def does_include_path(self, path):
        '''
        Must be same as:

            return path in self.get_all_paths()

        (Which is the default implementation)

        You can implement something that is faster
        '''
        return path in map(normalize_path, self.get_all_paths())
