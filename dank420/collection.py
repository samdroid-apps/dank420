import lookupy
from lookupy.dunderkey import dunder_get
import os
import glob

from . import view
from . import util


class Item():
    '''
    A basic item class

    It is a bit of a convenience, as it allows constructor **kwargs to be
    set as attributes

    It allows the __getitem__ interface (aka item['key']) to be identical to
    item.key.  This allows the Collection query things to work.
    '''

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)


class QueryOp():
    '''
    A query operator
    '''

    def apply(self, it):
        '''
        Apply operator to an iterator.  Returns an iterator
        '''
        return it


class _FilterQueryOp(QueryOp):
    def __init__(self, *args, **kwargs):
        q1 = list(args) if args else []
        q2 = [lookupy.Q(**kwargs)] if kwargs else []
        self._lookups = q1 + q2

    def apply(self, iterator):
        predicate = lambda item: all(l.evaluate(item) for l in self._lookups)
        return (x for x in iterator if predicate(x))


class _SortQueryOp(QueryOp):
    def __init__(self, reverse, *args):
        self._fields = args
        self._reverse = reverse

    def apply(self, iterator):
        key_fn = lambda item: tuple((dunder_get(item, f) for f in self._fields))
        list_ = sorted(iterator, key=key_fn, reverse=self._reverse)
        return iter(list_)


class CollectionView():
    '''
    A ""view"" over a collection object.

    Implements the filter and other operations;
    '''
    def __init__(self, parent=None, query: QueryOp = None):
        self._parent = parent
        self._query = query

    # This could actually be a bad idea; as some methods of the
    # parent view might iterate over the collection or something
    def __getattr__(self, name):
        if self._parent is not None:
            return getattr(self._parent, name)
        else:
            return super(self).__getattr__(name)

    def all(self):
        '''
        Identity operation
        '''
        return CollectionView(parent=self)

    def filter(self, *args, **kwargs):
        '''
        Create a filtered view of the collection

        Args:
            args - `lookpy.Q` query objects
            kwargs - arguments to construct a single lookupy.Q object.

        Returns:
            A CollectionView with the filter applied
        '''
        op = _FilterQueryOp(*args, **kwargs)
        return CollectionView(parent=self, query=op)

    def sort(self, *args, reverse=False):
        '''
        Create a sorted view of the collection

        Args:
            args (str) - a list of fields to use as a sort key
            reverse (boolean) - if the sort should be reversed

        Return:
            A CollectionView with the sort applied
        '''
        op = _SortQueryOp(reverse, *args)
        return CollectionView(parent=self, query=op)

    def __iter__(self):
        iterator = iter(self._parent)
        if self._query is not None:
            iterator = self._query.apply(iterator)
        return iterator


class Collection(CollectionView):
    '''
    Represents a list of items

    A subclass must implement the following methods:

        load
        __iter__

    A collection could implement the other methods

        register_reloader
    '''

    def load(self):
        '''
        Reload the collection 
        '''
        raise NotImplementedError('Collection subclass must implement load')

    def register_reloader(self, site):
        '''
        Register hooks for reloading the collection (for example,
        this is called when the dev server is running)

        Args:

            site (`dank420.Site`) - the site to register the reloader for
        '''
        pass

    def __iter__(self):
        '''
        Return an iterator of Items in the collection
        '''
        raise NotImplementedError('Collection subclass must implement __iter__')



class ItemPerPageView(view.View):
    '''
    A view where every page is an item from a collection

    Attributes:
        collection (CollectionView) - the collection instance
    '''

    def get_path_for_item(self, item):
        '''
        Get the path for a given item

        Returns:
            string, URL path for an item

        Example:

            def get_path_for_item(self, item):
                return f'/blog/{item.id}'
        '''
        raise NotImplementedError(
                'CollectionPerPageView subclass must implement get_path_for_item')

    def get_item_for_request(self, request):
        '''
        Get the item for the current request

        Returns:
            any, an item from the collection

        Raises:
            ValueError if request is insane
        '''
        path = util.normalize_path(request.path)
        for item in self.collection:
            ipath = util.normalize_path(self.get_path_for_item(item))
            if ipath == path:
                return item
        raise ValueError(f'Invalid path {path} is not in collection')

    def get_all_paths(self):
        return [self.get_path_for_item(item) for item in self.collection]

    @classmethod
    def on_registered(cls, site):
        cls.collection.load()
        cls.collection.register_reloader(site)


class FileCollectionItem(Item):
    '''
    Customized item for use in a file collection.

    Records the filename

    Args:
        fname (string): Filename that this object should load and represent
        kwargs (dict): Should pass down to super

    Superclasses **must** call `super().__init__(fname, **kwargs)`
    '''

    def __init__(self, fname, **kwargs):
        super().__init__(**kwargs)
        self.filename = fname


class FileCollection(Collection):
    '''
    A collection that is backed by files that match the path glob

    Attributes:
        path (str): a glob path to find the files, for example `./posts/**`
        Item (FileCollectionItem superclass): the class for the items

    Note that this collection does not provide any ordering on the items.  It
    can even changes as reloads happen.  You should use the `.sort` function
    to get a sorted view of this collection.
    '''
    Item = FileCollectionItem

    def __init__(self, **kwargs):
        assert issubclass(self.Item, FileCollectionItem)
        assert self.path

        super(**kwargs)
        self._items = []

    def load(self):
        self._items = []
        for fname in glob.iglob(self.path):
            self._items.append(self.Item(fname))

    def register_reloader(self, site):
        site.register_reload_callback(self._reload_cb, self.path)

    def _reload_cb(self, path):
        if not os.path.isfile(path):
            return

        self._items = [i for i in self._items if
                os.path.abspath(i.filename) != os.path.abspath(path)]
        self._items.append(self.Item(path))

    def __iter__(self):
        return iter(self._items)
