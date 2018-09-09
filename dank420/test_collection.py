import pytest
import tempfile

from .request import Request
from .collection import (Collection, Item, ItemPerPageView,
        FileCollection, FileCollectionItem, DoNotLoadException)

def test_collection_raises():
    c = Collection()
    with pytest.raises(NotImplementedError):
        c.load()
    with pytest.raises(NotImplementedError):
        iter(c)
    with pytest.raises(NotImplementedError):
        for x in c:
            print(x)


class BasicCollection(Collection):
    class Item(Item):
        pass

    def load(self):
        pass

    def __iter__(self):
        return iter([
            self.Item(a=10, b=2), self.Item(a=20, b=1), self.Item(a=30, b=3)])

def test_collection_item():
    c = BasicCollection()
    l = list(c)
    assert l[0]['a'] == 10
    assert l[0].a == 10
    assert l[0]['b'] == 2
    assert l[0].b == 2


def test_collection_filter():
    c = BasicCollection()
    v = c.filter(a__exact=10)
    items = list(iter(v))
    assert len(items) == 1
    assert items[0].a == 10
    assert items[0].b == 2

    v2 = c.filter(a__gt=15).filter(b__gte=1)
    items = list(iter(v2))
    assert len(items) == 2
    assert items[0].a == 20
    assert items[1].a == 30


def test_collections_all():
    c = BasicCollection()
    items = list(c)

    v = c.all()
    items2 = list(v)

    for x, y in zip(items, items2):
        assert x.a == y.a
        assert x.b == y.b


def test_collections_sort():
    c = BasicCollection()
    sort = c.sort('b', 'a')
    items = list(sort)

    sortr = c.sort('b', 'a', reverse=True)
    items2 = list(reversed(list(sortr)))

    for il in [items, items2]:
        assert il[0].b == 1
        assert il[0].a == 20
        assert il[1].b == 2
        assert il[1].a == 10
        assert il[2].b == 3
        assert il[2].a == 30

def test_collections_filter_sort():
    c = BasicCollection()
    v2 = c.filter(a__gt=15).sort('a')
    items = list(v2)
    assert len(items) == 2
    assert items[0].a == 20
    assert items[1].a == 30


def test_item_per_page_view():
    class View(ItemPerPageView):
        collection = BasicCollection()

        def get_path_for_item(self, item):
            return f'/c/{item.a}'

    v = View()
    paths = v.get_all_paths()
    assert paths == ['/c/10', '/c/20', '/c/30']

    item = v.get_item_for_request(Request('/c/20', None))
    assert item.a == 20
    assert item.b == 1

    with pytest.raises(ValueError):
        item = v.get_item_for_request(Request('/c/50', None))

def test_file_collection():
    with tempfile.TemporaryDirectory() as dirname:
        with open(f'{dirname}/A', 'w') as f:
            f.write('A')
        with open(f'{dirname}/B', 'w') as f:
            f.write('B')

        class MyFileCollectionItem(FileCollectionItem):
            def __init__(self, fname):
                with open(fname, 'r') as f:
                    char = f.read().strip()

                super().__init__(fname, char=char)

        class MyFileCollection(FileCollection):
            path = f'{dirname}/*'
            Item = MyFileCollectionItem

        c = MyFileCollection().sort('char')
        c.load()

        l = list(c)
        assert len(l) == 2
        assert l[0].char == 'A'
        assert l[1].char == 'B'


def test_file_collection_with_do_not_load():
    with tempfile.TemporaryDirectory() as dirname:
        with open(f'{dirname}/A', 'w') as f:
            f.write('A')
        with open(f'{dirname}/B', 'w') as f:
            f.write('B')

        class MyFileCollectionItem(FileCollectionItem):
            def __init__(self, fname):
                with open(fname, 'r') as f:
                    char = f.read().strip()

                if char == 'B':
                    raise DoNotLoadException

                super().__init__(fname, char=char)

        class MyFileCollection(FileCollection):
            path = f'{dirname}/*'
            Item = MyFileCollectionItem

        c = MyFileCollection()
        c.load()

        l = list(c)
        assert len(l) == 1
        assert l[0].char == 'A'
