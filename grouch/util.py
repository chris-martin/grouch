from itertools import zip_longest
import os, os.path
import string


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def character_whitelist(x, whitelist):
    return x.translate(None, string.maketrans(
        whitelist, ' ' * len(whitelist)
    ))


def grouper(n, iterable, fillvalue=None):
    """
    Collects data into fixed-length chunks or blocks.

        >>> grouper(3, 'ABCDEFG', 'x')
        'ABC DEF Gxx'
    """
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
