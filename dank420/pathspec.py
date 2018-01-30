import re

class Pathspec():
    '''
    Pathspec: a class to manage patterns for matching and creating paths


    Pathspecs are made from strings.  Strings are kept verbatim, and
    variables are enclosed in angular brackets.

    Examples:

        /blog/<post> - would match things like /blog/hello
        /static/<*filename> - the * means the matched section can include "/",
            for example it would match /static/css/main.css AND /static/main.css
    '''

    def __init__(self, pathspec):
        variable_re = r'<(?P<mod>\*?)(?P<name>[a-zA-Z_]\w+)>'
        def repl(match):
            name = match.group('name')
            mod = match.group('mod')
            if '*' in mod:
                return '(?P<'+name+'>.+)'
            else:
                return '(?P<'+name+'>[^/]+)'

        regex = re.sub(variable_re, repl, pathspec)
        regex = '^' + regex + '$'
        self._regex = re.compile(regex)

        def repl(match):
            name = match.group('name')
            return '{'+name+'}'
        self._format = re.sub(variable_re, repl, pathspec)

    def match(self, path):
        '''
        Match a path to this format

        Returns dict of name->value pairs (str->str)
        or None if no match was found
        '''
        match = self._regex.match(path)
        if match is None:
            return None
        return match.groupdict()

    def format(self, **kwargs):
        '''
        Substitute the kwargs into the URL

        Returns:
            sting, formatted url
        '''
        return self._format.format(**kwargs)


