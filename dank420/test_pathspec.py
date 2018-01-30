from .pathspec import Pathspec

def test_pathspec_to_regex_static():
    ps = Pathspec('/')
    assert ps.match('/') is not None
    assert ps.match('/home') is None

    ps = Pathspec('/home')
    assert ps.match('/') is None
    assert ps.match('/home') is not None


def test_pathspec_to_regex_dynamic():
    re = Pathspec('/blog/<post>')
    assert re.match('/') is None
    assert re.match('/blog/') is None
    match = re.match('/blog/hello')
    assert match == {'post': 'hello'}

    re = Pathspec('/blog/<post>/<view>')
    assert re.match('/') is None
    assert re.match('/blog/') is None
    assert re.match('/blog/hello/') is None
    match = re.match('/blog/hello/full')
    assert match == {'post': 'hello', 'view': 'full'}


def test_pathspec_to_regex_dynamic_star():
    re = Pathspec('/blog/<*post>')
    assert re.match('/') is None
    assert re.match('/blog/') is None
    match = re.match('/blog/hello')
    assert match == {'post': 'hello'}
    match = re.match('/blog/hello/more')
    assert match == {'post': 'hello/more'}

def test_pathspec_format():
    ps = Pathspec('/blog/<post>')
    assert ps.format(post='hello') == '/blog/hello'
    ps = Pathspec('/blog/<*post>')
    assert ps.format(post='hello/y') == '/blog/hello/y'
    ps = Pathspec('/<blog>/<post>')
    assert ps.format(blog='blog1', post='hello') == '/blog1/hello'
