def force_response(data):
    '''
    Force a value returned by a view (str, bytes, etc.) to be a
    Response object.

    For Response objects, this is an identity function
    (aka. force_response(response) == response for all Response objects)

    Returns: Response

    Raises: ValueError
    '''
    if isinstance(data, str):
        data = data.encode('utf8')
    if isinstance(data, bytes):
        data = Response(data)
    if isinstance(data, Response):
        return data
    raise ValueError('View should return Response, str or bytes, got: {}'.format(data))


class Response():
    '''
    Object representing the response of the view.

    Responses have data (which must be bytes)

    The content_type value is only advisory.  It is used on the development
    server, and informs the building process (eg. when transforming
    /about into /about/index.html).  However, in production, the server
    will guess the content type (or whatever you configure nginx/apache/etc
    to do)

    Attributes:
        data (bytes): the content of the response
        content_type (str): advisory content type value
    '''
    def __init__(self, data, content_type='text/html'):
        if not isinstance(data, bytes):
            raise ValueError(f'Data must be bytes; got {data}')
        self.data = data
        self.content_type = 'text/html'

    @property
    def is_html(self):
        '''
        Returns True if the response is HTML, otherwise false
        '''
        return self.content_type == 'text/html'


