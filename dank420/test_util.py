from . import util

def test_normalize_path():
    assert util.normalize_path('/') == '/'
    assert util.normalize_path('/home') == '/home'
    assert util.normalize_path('/home/') == '/home'
    assert util.normalize_path('/bro/mate') == '/bro/mate'
    assert util.normalize_path('/bro/mate/') == '/bro/mate'
    assert util.normalize_path('/bro/mate//') == '/bro/mate'

def test_slugify_grow():
    # Test with a series of examples from my blog, which was previously
    # using grow.io
    cases = [
        ('Gtk+ 3.22 theme support',
            'gtk+-3-22-theme-support'),
        ('A Grow.io Introduction',
            'a-grow-io-introduction'),
        ('Liberating Presenter Club',
            'liberating-presenter-club'),
        ('Environments with Nix Shell - Learning Nix pt 1',
            'environments-with-nix-shell-learning-nix-pt-1'),
        ('How they track you: Email Service Provider Edition',
            'how-they-track-you:-email-service-provider-edition'),
        ('6 Stunning Email SignUp Form Designs with Free HTML',
            '6-stunning-email-signup-form-designs-with-free-html'),
        ('My WATCH runs GNU/Linux And It Is Amazing',
            'my-watch-runs-gnu-linux-and-it-is-amazing')]
    for value, expected in cases:
        assert util.slugify_grow(value) == expected
