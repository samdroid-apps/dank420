from . import util

def test_normalize_path():
    assert util.normalize_path('/') == '/'
    assert util.normalize_path('/home') == '/home'
    assert util.normalize_path('/home/') == '/home'
    assert util.normalize_path('/bro/mate') == '/bro/mate'
    assert util.normalize_path('/bro/mate/') == '/bro/mate'
    assert util.normalize_path('/bro/mate//') == '/bro/mate'
