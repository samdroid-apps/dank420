class Request():
    '''
    Request object

    It provides access to the `Site` object through the `site` attribute

    It provides access to the path through the `path` attribute
    '''
    def __init__(self, path, site):
        self.path = path
        self.site = site


