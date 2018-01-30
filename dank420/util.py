
def normalize_path(path):
    '''
    Remove trailing slashes; they aren't useful in a static server context
    '''
    if path == '/':
        return '/'
    return path.rstrip('/')


