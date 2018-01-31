import re

def normalize_path(path):
    '''
    Remove trailing slashes; they aren't useful in a static server context
    '''
    if path == '/':
        return '/'
    return path.rstrip('/')


_GROW_SLUG_REGEX = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify_grow(text, delim=u'-'):
    '''
    A function to convert some text into a URL slug (a string of characters
    that is URL safe)

    It is very similar to the one included in grow.io, although does have
    the same behaviour for non-ascii characters.  This is still useful
    if you are converting your site.

    Args:
        text (string): text to slugify
        delim (string): separator between words for slug output

    Returns:
        string, a url safe string, containing no slashes
    '''
    words = [word for word in _GROW_SLUG_REGEX.split(text.lower()) if word]
    return delim.join(words)

