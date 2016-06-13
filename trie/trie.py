from collections.abc import MutableMapping


class Trie(MutableMapping):
    """
    A prefix tree mapping keys to values, where each key must be an arbitrary
    sequence of hashable elements (usually a string) and values may be objects
    of any type or :None:

    >>> trie = Trie(she=1, sells=5, sea=10, shells=19, today=5)
    >>> print(*sorted(trie))
    sea sells she shells today

    >>> print(*sorted(trie.items()))
    ('sea', 10) ('sells', 5) ('she', 1) ('shells', 19) ('today', 5)

    >>> print(*trie.keys(prefix='sh'))
    she shells

    >>> trie['today'] = -55
    >>> trie['today']
    -55

    >>> len(trie)
    5

    >>> 'shells' in trie, 'shore' in trie
    (True, False)

    >>> del trie['shells']
    >>> len(trie)
    4
    """

    def __init__(self, *args, **kwargs):
        """
        Create a new Trie initialized from an optional iterable of key value pairs or keys
        and a possibly empty set of keyword arguments, as for the built-in :dict: type.
        """
        self._root = _Entry()
        self._length = 0
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        """
        Gets the value corresponding to the specified key.

        :param key: an iterable
        :return: the value corresponding to the key if it is in the Trie,
        raising a KeyError otherwise.
        """
        entry = self._find(key)
        if entry.has_value():
            return entry.value
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Sets or inserts the specified value, mapping the specified key to it

        :param key: an iterable to update or insert
        :param value: the object to associate with the key
        """
        entry = self._find(key, create=True)
        self._set_entry(entry, value)

    def __delitem__(self, key):
        """
        Removes the value of the specified key from the Trie

        :param key: the iterable whose value is to be removed
        """
        entry = self._find(key)
        if entry.has_value():
            del entry.value
            self._length -= 1
        else:
            raise KeyError(key)

    def __len__(self):
        return self._length

    def __iter__(self):
        return iter(self.keys())

    def __repr__(self):
        pairs = ('{}={}'.format(key, value) for key, value in self.items())
        return 'Trie({})'.format(', '.join(pairs))

    def keys(self, prefix=''):
        """
        Searches for keys beginning with the specified prefix

        :param prefix: an iterable
        :return: A generator yielding the keys one by one, as they are found
        """
        return (key for key, value in self.items(prefix))

    def items(self, prefix=''):
        """
        Searches for key value pairs where the keys begin with the specified prefix

        :param prefix: an iterable
        :return: A generator yielding tuples of keys and values as they are
        found
        """
        try:
            start = self._find(prefix)
        except KeyError:
            raise StopIteration
        stack = [(prefix, start)]
        while stack:
            current_prefix, entry = stack.pop()
            if entry.has_value():
                yield current_prefix, entry.value
            for char, children in entry.items():
                stack.append((current_prefix + char, children))

    def transform(self, key, value_selector, default=None):
        """
        Updates key with the value obtained from the value selector function,
        to which the old value corresponding to the key is passed.

        :param key: the key whose value is to be updated
        :param value_selector: a function that takes the old value as an argument and returns a new value
        :param default: the value to pass to value_selector if there is no previous value
        """
        entry = self._find(key, create=True)
        value = value_selector(entry.value if entry.has_value() else default)
        self._set_entry(entry, value)

    def _find(self, key, *, create=False):
        entry = self._root
        for char in key:
            if char in entry:
                entry = entry[char]
            elif create:
                new_entry = _Entry()
                entry[char] = new_entry
                entry = new_entry
            else:
                raise KeyError(key)
        return entry

    def _set_entry(self, entry, value):
        if not entry.has_value():
            self._length += 1
        entry.value = value


class _Entry(dict):
    """
    A dictionary, with an optional :value: attribute, representing an entry
    in the :Trie: data structure.
    """

    def has_value(self):
        """
        Indicates whether this entry is considered an endpoint, i.e. has a value assigned to it.
        :return: True if :value: is set, otherwise False
        """
        return hasattr(self, 'value')
